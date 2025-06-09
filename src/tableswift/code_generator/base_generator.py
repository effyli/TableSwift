import os
import openai
from openai import OpenAI
from together import Together
import instructor
from pydantic import BaseModel
from ollama import chat
from ollama import ChatResponse

from abc import ABC
from ..promptsTemplate import get_prompts_set, PromptTemplate

class CodeGenerator(ABC):
    """
    All functions here are programming language independent.
    """
    def __init__(self, task: str, llm: str, api_key: str) -> None:
        super().__init__()
        self.lang = None
        self.use_data_router = None
        self.task = task
        # it can be ["gpt-4-turbo", "llama3.2", "qwen2.5-coder"]
        self.llm = llm
        self.prompts_set = None
        self.api_key = api_key

        # pre-defined categories
        self.openai_models = {"gpt-4": "gpt-4-turbo", "gpt-4o-mini": "gpt-4o-mini"}
        # openrouter models
        self.openrouter_models = {"deepseek-r1": "deepseek/deepseek-r1:free"}
        # llama3.2: llama3.2-3b-instruct, qwen2.5-coder: qwen2.5-coder-7b
        # ollama is completely local and free
        self.ollama_models = {"llama3.2-3b": "llama3.2", "qwen2.5-coder-7b": "qwen2.5-coder"}
        # llama3.1-405b
        self.together_models = {"llama3.1-405b": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", 
                                "llama3.1-70b": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                                "qwen2.5-coder-32b": "Qwen/Qwen2.5-Coder-32B-Instruct",
                                "llama3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                                "llama3.2-3b": "meta-llama/Llama-3.2-3B-Instruct-Turbo"}
    
    def formulate_prompt(self, instruction: str, examples: str):
        prompts_set = get_prompts_set(self.lang, use_data_router=self.use_data_router)
        if self.task == "data_transformation":
            template_name = "STRING_TRANSFORMATION"
        elif self.task == "entity_matching":
            template_name = "ENTITY_MATCHING"
        elif self.task == "data_imputation":
            template_name = "DATA_IMPUTATION"
        elif self.task == "error_detection_spelling":
            template_name = "ERROR_DETECTION_SPELLING"
        else:
            raise NotImplementedError
        prefix = prompts_set["TASK_PREFIX"]
        if template_name not in prompts_set:
            raise NotImplementedError
        else:
            template = prompts_set[template_name]
        prompts = prefix + template
        prompt_template = PromptTemplate(prompt=prompts)
        prompts = []
        for prompt_t in prompt_template.prompt:
            prompt = prompt_t.copy()
            if 'user' in prompt_t['role']:
                print("Found user")
                prompt['content'] = prompt['content'].format(instruction=instruction, examples=examples)
            prompts.append(prompt)
        self.prompts_set = prompts_set
        return prompts, prompt_template
    

    def call_llm(self, messages, response_model):
        print(self.llm)
        if self.llm in self.openrouter_models:
            model_name = self.openrouter_models[self.llm]
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            # Extract structured data from natural language
            response = client.chat.completions.create(
                model=model_name,
                messages=messages)
            structured_output = response.choices[0].message.content
            print("structured output   ", structured_output)
        elif self.llm in self.openai_models:
            model_name = self.openai_models[self.llm]
            client = instructor.from_openai(client = openai.OpenAI(api_key=self.api_key),)

            # Extract structured data from natural language
            structured_output = client.chat.completions.create(
                model=model_name,
                response_model=response_model,
                messages=messages,
            )
        elif self.llm in self.ollama_models:
            # not using instructor here because it doesn't work well with smaller models
            # enables `response_model` in create call
            # client = instructor.from_openai(
            #     OpenAI(
            #         base_url="http://localhost:11434/v1",
            #         api_key="ollama",  # required, but unused
            #     ),
            #     mode=instructor.Mode.JSON,
            # )
            # resp = client.chat.completions.create(
            #     model="llama3.2",
            #     messages=messages,
            #     response_model=response_model,
            # )
            model_name = self.ollama_models[self.llm]
            response: ChatResponse = chat(model=model_name, messages=messages)
            structured_output = response['message']['content']
            print(f"structured output   {structured_output}")
        elif self.llm in self.together_models:
            model_name = self.together_models[self.llm]
            client = Together(api_key=self.api_key)

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
            )
            structured_output = response.choices[0].message.content
            print(f"structured output   {structured_output}")
        else:
            raise NotImplementedError
        
        return structured_output

    def post_process():
        pass

    def execute():
        """
        Taking a piece of code string, try to execute it. Return true if it is executable.
        """
        pass

    def validate(self, fn, test_data, supervision_data, threshold_sup=10., threshold=0.51):
        """
        We validate function by checking:
        1. If the function runs.
        2. If the function get ~100% [self-defined] accuracy on the demonstrations.
        3. [Optional]If the function is generalizable by prompting LLMs. (currently not supported).
        """
        runnable, msg = self.execute(fn, test_data)
        if not runnable:
            error_message = f"The generated code {fn} is not excutable, error message is {msg}. Please fix the code."
            return "not_excutable", error_message, 0
        acc, _ = self.evaluate(fn, test_data)
        # we don't expect accuracy to be 100% on currency exchange tasks
        if acc < threshold:
            error_message = f"The generated code {fn} only achieves {acc} accuracy on provided examples. Please provide different code to achieve higher accuracy."
            return "not_fit", error_message, acc
        if supervision_data and not len(supervision_data) == 0:
            acc_sup, _ = self.evaluate(fn, supervision_data)
            if acc_sup < threshold_sup:
                error_message = f"The generated code {fn} is overfitting on the provided example, please reconsider the intention of this task."
                return "not_generalizable", error_message, acc
        return "validated", "", acc

    def evaluate():
        pass

    def pipeline():
        # here we have the logic of generate, validate, rank and omit
        pass