# do we really want to do execution in the ts framework?
from ..code_generator import PythonGenerator, SQLGenerator
from ..llm_pr.llmpr import LLMPR

def execute_code_logic(code: str, lang: str, inputs: list,
                       instruction: str, 
                       demonstrations: list, task: str,
                       hyperparams: dict, api_key: str, router_code: str = None) -> None:
    """
    Execute the generated code.
    """
    print("Executing code logic...")
    print(f"Executing Code: {code}")
    print(f"Language: {lang}")
    print(f"Router Code: {router_code}")

    llm = hyperparams["llm"]
    use_data_router = hyperparams["use_data_router"]
    max_num_solutions = hyperparams["max_num_solutions"]
    limit_fallback = hyperparams["limit_fallback"]

    transformation_data = []
    if lang == "python":
        generator = PythonGenerator(task=task, llm=llm, use_data_router=use_data_router, api_key=api_key)
    elif lang == "sql":
        generator = SQLGenerator(task=task, llm=llm, use_data_router=use_data_router, api_key=api_key)
    else:
        raise NotImplementedError(f"Language {lang} is not supported for execution.")
    # inputs should be a list of dictionaries that shows {"Input": "sample1", "Output": ""}
    valid_data, invalid_data = generator.route_data(router_code, inputs)
    # invalid_data_per_batch.append(invalid_data)
    for sample in valid_data:
        sample_input = sample["Input"]
        result = generator.execute_function_string(code, sample_input)
        sample["Output"] = result
        transformation_data.append(sample)
    # valid_data should be a list of dictionaries that shows {"Input": "sample1", "Output": "label1"}
    # there is still logic on how to handle invalid data and defining the maximum number of solutions
    if len(invalid_data) == 0:
        print("All samples were successfully processed.")
    elif len(invalid_data) <= limit_fallback:
        print(f"Fallback triggered: {len(invalid_data)} invalid samples left, within the limit of {limit_fallback}.")
        # fall back to LLMPR
        llm_pr = LLMPR(task=task, api_key=api_key, model_name=llm)
        transformed_samples = llm_pr.pipeline_no_eval(instruction, demonstrations, invalid_data)
        transformation_data.extend(transformed_samples)
    else:
        print(f"Too many invalid samples left: {len(invalid_data)}, should generate another code.")
    return transformation_data, invalid_data