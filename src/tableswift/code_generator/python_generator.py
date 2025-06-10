import ast
import openai
import sys
import logging
import multiprocessing
sys.path.insert(0, '')

from ..utils import function_utils
from ..utils.formatter_utils import format_model_output_python
from .base_generator import CodeGenerator
from pydantic import BaseModel, Field

print(function_utils)

logger = logging.getLogger(__name__)

class PythonResponse(BaseModel):
    reasoning: str
    python_code: str

class PythonResponse_DataRouter(BaseModel):
    reasoning: str
    solving_task_code: str
    validate_code: str

class PythonGenerator(CodeGenerator):
    def __init__(self, task: str, llm: str, use_data_router:bool, api_key:str) -> None:
        super().__init__(task, llm, api_key)
        self.lang = "python"
        self.use_data_router = use_data_router

    def get_response(self, messages):
        """
        We use instructor and pre-defined response model
        """
        print("here is the complete messages, ", messages)
        response_model = PythonResponse if not self.use_data_router else PythonResponse_DataRouter
        structured_output = self.call_llm(messages, response_model)
        if self.llm in self.ollama_models or self.llm in self.together_models or self.llm in self.openrouter_models:
            structured_output = format_model_output_python(structured_output)
            print("Structured output after formatting: ", structured_output)
        return structured_output

    def pre_process(self, input: str):
        if isinstance(input, str):
            input = input.replace("'", "''")
        return input
    
    def post_process(self, structured_output):
        """
        Post process the structured output, return a dictionary
        This is the same for both code generators
        """
        result = {"resoning": None, "transformation_code": None, "validation_code": None}
        if self.llm in self.ollama_models or self.llm in self.together_models or self.llm in self.openrouter_models:
            result["transformation_code"] = structured_output
            return result
        if not self.use_data_router:
            try:
                reasoning = structured_output.reasoning
                result["reasoning"] = reasoning
                transformation_code = structured_output.python_code
                if transformation_code:
                    transformation_code = transformation_code.replace('\\\\', '\\')
                    result["transformation_code"] = transformation_code
            except:
                pass
            return result
        else:
            try:
                reasoning = structured_output.reasoning
                result["reasoning"] = reasoning
                transformation_code = structured_output.solving_task_code
                validation_code = structured_output.validate_code
                if transformation_code:
                    transformation_code = transformation_code.replace('\\\\', '\\')
                    result["transformation_code"] = transformation_code
                if validation_code:
                    validation_code = validation_code.replace('\\\\', '\\')
                    result["validation_code"] = validation_code
            except:
                pass
            return result
    
    # def execute_function_string(self, fn, input_string, fn_type="transformation"):
    #     # TODO: parse to get the function name.
    #     # Prepare a custom namespace for executing the dynamic code. This can be an empty dict.
    #     if fn_type == "transformation":
    #         if self.task == "data_transformation":
    #             fn_name = "string_transformation"
    #         elif self.task == "entity_matching":
    #             fn_name = "entity_matcher"
    #         elif self.task == "data_imputation":
    #             fn_name = "impute_data"
    #         elif self.task == "error_detection_spelling":
    #             fn_name = "detect_error"
    #         else:
    #             raise NotImplementedError
    #     elif fn_type == "validation":
    #         fn_name = "validate"
    #     else:
    #         raise NotImplementedError
        
    #     namespace = {}
    #     # Execute the dynamic code. This will define the function within the 'namespace'.
    #     exec(fn, namespace)
    #     # Access the function from the namespace and call it
    #     func = namespace[fn_name]
    #     result = func(input_string) 
    #     return result
    
    # def execute(self, fn, test_data, fn_type="transformation"):
    #     try:
    #         _ = self.execute_function_string(fn, test_data[0]['Input'], fn_type)
    #     except Exception as e:
    #         return False, f"Error: {str(e)}"
    #     return True, "Execution successful."

    

    def execute_function_string(self, fn, input_string, fn_type="transformation"):
        """
        Executes a Python function string directly (no timeout logic here).
        """
        # Determine the function name based on the task and type
        if fn_type == "transformation":
            fn_name = {
                "data_transformation": "string_transformation",
                "entity_matching": "input_output_converter",
                "data_imputation": "input_output_converter",
                "error_detection_spelling": "detect_error",
            }.get(self.task, None)
        elif fn_type == "validation":
            fn_name = "validate"
        if not fn_name:
            raise NotImplementedError(f"Task '{self.task}' not supported.")

        # Prepare a custom namespace for executing the dynamic code
        namespace = {}
        exec(fn, namespace)  # Define the function in the namespace
        func = namespace[fn_name]  # Access the function by name
        return func(input_string)  # Call the function with input data
    
    def target_function(self, queue, fn, input_string, fn_type):
        """
        Executes the function string and puts the result and message in a queue.
        """
        try:
            result = self.execute_function_string(fn, input_string, fn_type=fn_type)
            queue.put((result, "Execution successful."))
        except Exception as e:
            queue.put((None, f"Error: {str(e)}"))

    def execute(self, fn, test_data, fn_type="transformation", timeout=5):
        """
        Wraps `execute_function_string` with timeout logic and returns both result and message.
        """
        if isinstance(test_data, list):
            input_string = test_data[0]['Input']
        elif isinstance(test_data, str):
            input_string = test_data
        queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=self.target_function,
            args=(queue, fn, input_string, fn_type)
        )

        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()  # Forcefully terminate the process
            process.join()
            return None, f"Error: Execution timed out after {timeout} seconds."

        # Retrieve the result and message from the queue
        if not queue.empty():
            return queue.get()
        return None, "Error: Execution failed: Unknown error."
    
    def evaluate(self, fn, test_data):
        inputs = [item["Input"] for item in test_data]
        outputs = [item["Output"] for item in test_data]
        predicted_outputs = []
        for input, output in zip(inputs, outputs):
            try:
                result, _ = self.execute(fn, input)
            except Exception as error:
                print(f"Error message: {error}")
                result = "Not excutable"
            predicted_outputs.append(result)
            print("pred: {}, gt: {}".format(result, output))
        # acc = calculate_accuracy(predicted=predicted_outputs, ground_truth=outputs)
        metrics = function_utils.compute_metrics(preds=predicted_outputs, golds=outputs, task=self.task)
        if self.task in [
                "data_imputation",
                "data_transformation",
                
            ]:
            acc = metrics[2]
        elif self.task in ["entity_matching", "error_detection_spelling"]:
            acc = metrics[3]
        print("The accuacry/f1 of the generated function is ", acc)
        return acc, predicted_outputs
    
    def route_data(self, v_fn, test_data):
        """
        Route the data given the response from the validation function
        """
        valid_data = []
        invalid_data = []
        if v_fn:
            inputs = [item["Input"] for item in test_data]
            outputs = [item["Output"] for item in test_data]
            for input, output in zip(inputs, outputs):
                try:
                    decision, _ = self.execute(v_fn, input, "validation")
                    logger.info(f"======> Decision for input {input} is {decision} <======")
                    print(f"======> Decision for input {input} is {decision} <======")
                    if decision:
                        valid_data.append({"Input": input, "Output": output})
                    else:
                        invalid_data.append({"Input": input, "Output": output})
                except Exception as error:
                    # if the validation function is not excutable, we treat it as valid data
                    print(f"Error message: {error}")
                    valid_data.append({"Input": input, "Output": output})
        else:
            valid_data = test_data
        return valid_data, invalid_data
    
    def pipeline_backbone(self, messages, examples, supervision_data, depth):
        """
        Pipeline for getting a valid transformation function
        """
        func = None
        num_iter = 1
        functions_stack = []
        result = None
        while num_iter <= depth:
            # getting the first function
            response = self.get_response(messages)
            result = self.post_process(response)
            if result["transformation_code"]:
                func = result["transformation_code"]
                decision, msg, acc = self.validate(func, examples, supervision_data)
                # for debugging
                print("The decision is ", decision)
                print("The message is ", msg)
                print("The accuracy is ", acc)

                if "not" in decision:
                    if not decision == "not_excutable":
                        functions_stack.append((func, acc))
                    # if this is the last try and the function runs then we return
                    if (num_iter == depth - 1):
                        if functions_stack:
                            # sort the function stack
                            sorted_func_stack = sorted(functions_stack, key = lambda x: x[1], reverse=True)
                            return (*sorted_func_stack[0], result)
                    # add error message and re-prompt
                    retry_msg = self.prompts_set["TASK_RETRY"][0].copy()
                    retry_msg['content'] = retry_msg['content'].format(error_message=msg)
                    messages.append(retry_msg)     
                else:
                    return (func, acc, result)           
            else:
                decision = "not parsable"
                msg = "The function calling return not parsable response, trying again!"
                acc = 0
                 # add error message and re-prompt
                retry_msg = self.prompts_set["TASK_RETRY"][0].copy()
                retry_msg['content'] = retry_msg['content'].format(error_message=msg)
                messages.append(retry_msg)   
            num_iter += 1
        return ("No function can be generated, please provide different demonstration!", float("-inf"), result)

    def pipeline_data_router(self, messages, examples, supervision_data, depth):
        """
        Pipeline with data router
        """
        # first prioritize the transformation code, after getting a valid transformation code, we then validate if the validation code is valid
        # for now we only valid the validation function but not re-generate
        # TODO: in the future we can re-generate the validation function
        t_func = None
        t_func, acc, result = self.pipeline_backbone(messages, examples, supervision_data, depth)
        if not t_func:
            return t_func, acc, None
        # now we validate the validation function
        v_func = result["validation_code"]
        if not v_func:
            return t_func, acc, None
        runnable, msg = self.execute(v_func, examples, "validation")
        if runnable:
            return t_func, acc, v_func
        else:
            return t_func, acc, None
        
    def pipeline(self, instruction, examples, supervision_data=None, depth: int=5):
        """
        The sequence of action for generating the final function is: generate function -> validate function -> correct function if necessary.
        """
        result = {"transformation_code": None, "acc": None, "validation_code": None}
        # Define the messages
        messages, _ = self.formulate_prompt(instruction=instruction, examples=function_utils.dicts_to_string(examples))   
        if not self.use_data_router:
            code, acc, _ = self.pipeline_backbone(messages, examples, supervision_data, depth)
            result["transformation_code"] = code
            result["acc"] = acc
        else:
            # use pipeline that contains data router
            code, acc, v_code = self.pipeline_data_router(messages, examples, supervision_data, depth)
            result["transformation_code"] = code
            result["acc"] = acc
            result["validation_code"] = v_code
        return result