# here we implement the fallback solution, using LLM on a per-row basis.
import copy
import openai
import logging
import instructor

from pydantic import BaseModel
from ..utils import function_utils


logger = logging.getLogger(__name__)

class LLMPRResponse(BaseModel):
    output: str

prefix_instr_dt = [{"role": "system", "content": "You are helpful assistant. Given the following input/output examples, figure out the transformation and generate the output when given input."}]
prefix_instr_em = [{"role": "system", "content": "You are helpful assistant. Given the following entities, figure out if entity A is the same with entity B. Yes or No?"}]
demonstration_instr = [{"role": "user", "content": f"""Instructions: {{instruction}}, Examples: {{examples}}, Input column name: {{column_name}}."""}]


class LLMPR:
    def __init__(self, model_name, task, api_key) -> None:
        self.model_name = model_name
        self.task = task
        self.api_key = api_key

    def formulate_prompt(self, instruction, examples, column_name=None):
        # print(f"Current demonstration template is ", demonstration_instr)
        prefix = []
        if self.task == "data transformation":
            prefix = copy.deepcopy(prefix_instr_dt)
        elif self.task == "entity matching":
            prefix = copy.deepcopy(prefix_instr_em)
        demonstration = copy.deepcopy(demonstration_instr)
        messages = prefix + demonstration
        for message in messages:
            if 'user' in message['role']:
                message['content'] = message['content'].format(instruction=instruction, examples=examples, column_name=column_name) 
        return messages

    def call_llm(self, message_row):
        # we run the LLM on the invalid rows
        client = instructor.from_openai(client = openai.OpenAI(api_key=self.api_key))
        # Extract structured data from natural language
        structured_output = client.chat.completions.create(
            model=self.model_name,
            response_model=LLMPRResponse,
            messages=message_row,
        )
        return structured_output
    
    def execute(self, messages, test_data):
        """
        We run the LLM on the invalid rows, and return results. No gts.
        """
        transformed_data = []
        for row in test_data:
            message_row = copy.deepcopy(messages) + [{"role": "user", "content": f"Input: {row['Input']}\nOutput:"}]
            structured_output = self.call_llm(message_row)
            if structured_output.output:
                output_pred = structured_output.output.lower().strip()
            else:
                output_pred = structured_output.output
            row['Output'] = output_pred
            transformed_data.append(row)
        return transformed_data
        
    def evaluate(self, messages, test_data):
        all_outputs_preds = []
        all_outputs_gt = []
        logger.info(f"prompts with demonstrations {messages}")
        for row in test_data:
            message_row = copy.deepcopy(messages) + [{"role": "user", "content": f"Input: {row['Input']}\nOutput:"}]
            structured_output = self.call_llm(message_row)
            if row['Output']:
                output_row = row['Output'].lower().strip()
            else:
                output_row = row['Output']
            if structured_output.output:
                output_pred = structured_output.output.lower().strip()
            else:
                output_pred = structured_output.output
            logger.info(f"====> Input: {row['Input']}, gt: {output_row}, pred: {output_pred} <===")
            all_outputs_preds.append(output_pred)
            all_outputs_gt.append(output_row)
        return all_outputs_gt, all_outputs_preds

    def pipeline(self, instructions, examples, test_data):
        """
        We run the LLM on the invalid rows, and then calculate the accruacy.
        """
        logger.info(f"Running fallback solution on {len(test_data)} invalid rows")
        examples=function_utils.dicts_to_string(examples)
        messages = self.formulate_prompt(instructions, examples)
        gts, preds = self.evaluate(messages, test_data)
        return gts, preds
    
    def pipeline_no_eval(self, instruction, column_name, examples, test_data):
        """
        Inference piopeline without evaluation.
        """
        print("LLMPR pipeline without evaluation")
        if examples:
            examples=function_utils.dicts_to_string(examples)
        else:
            examples = ""
        messages = self.formulate_prompt(instruction, examples, column_name)
        transformed_data = self.execute(messages, test_data)
        return transformed_data



        
        