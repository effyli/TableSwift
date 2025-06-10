from ..code_generator.python_generator import PythonGenerator
from ..code_generator.sql_generator import SQLGenerator
import numpy as np

def generate_code_logic(lang:str, task:str, instruction:str, 
                        samples:list, api_key:str, hyperparams:dict):
    functions_pool = []
    router_functions_pool = []
    perfs = []
    use_data_router = hyperparams["use_data_router"]
    num_trials = hyperparams["num_trials"]
    num_retry = hyperparams["num_retry"]
    seed = hyperparams["seed"]
    num_iter = hyperparams["num_iterations"]
    llm = hyperparams["llm"]

    if lang == "python":
        generator = PythonGenerator(task=task, llm=llm, use_data_router=use_data_router, api_key=api_key)
        if task == "data_transformation":
            dummy_func = "def string_transformation(input_string): return None"
        elif task == "entity_matching":
            dummy_func = "def entity_matcher(input_string): return None"
        elif task == "data_imputation":
            dummy_func = "def impute_data(input_string): return None"
        elif task == "error_detection_spelling":
            dummy_func = "def detect_error(input_string): return None"
        else:
            raise NotImplementedError
    elif lang == "sql":
        generator = SQLGenerator(task=task, llm=llm, use_data_router=use_data_router, api_key=api_key)
        dummy_func = "SELECT 'None'"
    else:
        raise NotImplementedError
    # We do N trials 
    for trial_num in range(num_trials):
        seed = seed + trial_num
        np.random.seed(seed)
        num_try = 0
        acc = None
        t_func = "No function"
        v_func = None
        while "No function" in t_func:
            if num_try >= num_retry:
                # use dummy function string
                t_func = dummy_func
                continue
            # samples should be a list of dictionaries that shows {""input": "sample1", "output": "label1"}
            demonstrations = samples
            # demonstrations, demon_df = sample_demonstrations(args, task, train_data)
            result = generator.pipeline(instruction=instruction, examples=demonstrations, depth=num_iter)
            t_func = result["transformation_code"]
            v_func = result["validation_code"]
            acc = result["acc"]
            num_try += 1
            seed += 1234
            np.random.seed(seed)
        if use_data_router:
            router_functions_pool.append(v_func)
        functions_pool.append(t_func)
        perfs.append(acc)
        # logger.info("Learned function for trial {} is {}".format(trial_num, t_func))
        # if use_data_router:
            # logger.info("Validation function is {}".format(v_func))
        
    # if there are multiple functions, we can use the one with the highest accuracy
    if len(functions_pool) > 1:
        best_idx = np.argmax(perfs)
        best_func = functions_pool[best_idx]
        if use_data_router:
            best_router_func = router_functions_pool[best_idx]
        else:
            best_router_func = None
    else:
        best_func = functions_pool[0]
        if use_data_router:
            best_router_func = router_functions_pool[0]
        else:
            best_router_func = None
    # logger.info("Best function is {}".format(best_func))
    # logger.info("Best router function is {}".format(best_router_func))
    return best_func, best_router_func