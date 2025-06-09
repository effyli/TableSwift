import json
import logging
import argparse
import numpy as np
import pandas as pd

from typing import List
from pathlib import Path
from utils.other_utils import setup_logger, compute_metrics
import utils.data_utils as data_utils
from code_generator import PythonGenerator, SQLGenerator
from llm_pr.llmpr import LLMPR


logger = logging.getLogger(__name__)

def sample_demonstrations(args, task, train_data):
    # we sample based on tasks
    if task in ["entity_matching", "error_detection_spelling"]:
        demonstrations, demon_df = data_utils.sample_data_stratified(train_data, args.k)
    elif task in ["data_transformation", "data_imputation"]:
        demonstrations, demon_df = data_utils.sample_data_random(train_data, args.k) 
    else:
        raise NotImplementedError
    logger.info(demonstrations)
    return demonstrations, demon_df

def function_generation(args, train_data, instruction, task, llm: str="gpt-4-turbo", lang: str="sql"):
    saved_funcs = []
    saved_vfuncs = []
    saved_acc = []
    if lang == "python":
        generator = PythonGenerator(task=task, llm=llm, use_data_router=args.use_data_router)
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
        generator = SQLGenerator(task=task, llm=llm, use_data_router=args.use_data_router)
        dummy_func = "SELECT 'None'"
    else:
        raise NotImplementedError
    # We do N trials 
    for trial_num in range(args.num_trials):
        seed = args.seed + trial_num
        np.random.seed(seed)
        num_try = 0
        acc = None
        t_func = "No function"
        v_func = None
        while "No function" in t_func:
            if num_try >= args.num_retry:
                # use dummy function string
                logger.info("Using dummy function.")
                t_func = dummy_func
                continue
            demonstrations, demon_df = sample_demonstrations(args, task, train_data)
            result = generator.pipeline(instruction=instruction, examples=demonstrations, depth=args.num_iter)
            t_func = result["transformation_code"]
            v_func = result["validation_code"]
            acc = result["acc"]
            num_try += 1
            seed += 1234
            np.random.seed(seed)
        logger.info("Learned function for trial {} is {}".format(trial_num, t_func))
        if args.use_data_router:
            logger.info("Validation function is {}".format(v_func))
        
        saved_funcs.append(t_func)
        saved_vfuncs.append(v_func)
        saved_acc.append(acc)
    return saved_funcs, saved_vfuncs, saved_acc, generator, demonstrations, demon_df


def main():
    # get arguments
    parser = argparse.ArgumentParser(description="Run wrangler")
    parser.add_argument(
        "--data_dir",
        type=str,
        help="Which data directory to run.",
        required=True,
    )
    parser.add_argument(
        "--output_dir", type=str, help="Output directory.", default="outputs"
    )
    parser.add_argument("--k", type=int, help="Number examples in prompt", default=3)
    parser.add_argument("--d", type=int, help="Number examples for training a classifier", default=100)
    parser.add_argument("--num_iter", type=int, help="Number of iterations to sample from training data", default=5)
    parser.add_argument("--num_retry", type=int, help="Number of retry to LLM", default=1)
    parser.add_argument(
        "--num_run",
        type=int,
        help="Number examples to run through model.",
        default=-1,
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="Language used for code generation, either python or sql",
        default="sql",
    )
    parser.add_argument(
        "--llm",
        type=str,
        help="Language model used for code generation, can be openai or local",
        default="gpt-4-turbo",
    )
    parser.add_argument(
        "--num_trials",
        type=int,
        help="Number trials to run. Results will be averaged with variance reported.",
        default=1,
    )
    parser.add_argument(
        "--sample_method",
        type=str,
        help="Example generation method",
        default="random",
        choices=["random", "manual", "validation_clusters"],
    )
    parser.add_argument(
        "--class_balanced",
        help="Class balance training data. Good for classification tasks \
             with random prompts.",
        action="store_true",
    )
    parser.add_argument(
        "--use_data_router",
        help="Use data router for generating functions.",
        action="store_true",
    )
    parser.add_argument(
        "--use_fallback",
        help="Use LLMPR as fallback solution.",
        action="store_true",
    )
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument(
        "--sep_tok",
        type=str,
        help="Separate for attr: val pairs in row. Default is '^'.",
        default="^",
    )
    parser.add_argument(
        "--nan_tok",
        type=str,
        help="Token to represent nan entries. Default is 'nan'.",
        default="nan",
    )
    args = parser.parse_args()
    # Get absolute path
    args.data_dir = str(Path(args.data_dir).resolve())
    setup_logger(args.output_dir)
    logger.info(json.dumps(vars(args), indent=4))
    limit_fallback = 100
    
    llm = args.llm
    logger.info(f"Using LLM: {llm}")

    test_file = "test"

    # Read pandas DF datasets
    pd_data_files, task = data_utils.read_data(
        data_dir=args.data_dir,
        class_balanced=args.class_balanced,
        add_instruction=False,
        max_train_samples=-1,
        max_train_percent=-1,
        sep_tok=args.sep_tok,
        nan_tok=args.nan_tok,
    )
    logger.info(f"Task for the dataset is {task}")
    if test_file not in pd_data_files:
        raise ValueError(f"Need {test_file} data")

    train_data = pd_data_files["train"]
    test_data = pd_data_files[test_file]
    num_run = args.num_run
    instructions = []

    if isinstance(train_data, List):
        if args.num_run == -1:
            num_run = test_data[0].shape[0]
        num_run = min(num_run, test_data[0].shape[0])
        logger.info(f"Number of tasks is {len(train_data)}")
        logger.info(f"Train shape is {train_data[0].shape[0]}")
        logger.info(f"Test shape is {test_data[0].shape[0]}")
        logger.info(f"Running {num_run} examples for {args.num_trials} trials.")
        if "instructions" in pd_data_files:
            instructions = pd_data_files["instructions"]
        logger.info(f"Number of tasks is {len(instructions)}")

    elif isinstance(train_data, pd.DataFrame):
        if args.num_run == -1:
            num_run = test_data.shape[0]
        num_run = min(num_run, test_data.shape[0])
        logger.info(f"Train shape is {train_data.shape[0]}")
        logger.info(f"Test shape is {test_data.shape[0]}")
        logger.info(f"Running {num_run} examples for {args.num_trials} trials.")
        train_data = [train_data]
        test_data = [test_data]
        instruction = data_utils.read_instruction(args.data_dir)
        if instruction:
            instructions = [instruction]
        else:
            instructions = [""]

    task_metrics = {"prec": [], "rec": [], "f1": [], "acc": []}
    all_gts = []
    all_preds = []
    all_saved_funcs = []
    task_number = 0
    for train_data_pd, test_data_pd, instruction in zip(train_data, test_data, instructions):
        task_number += 1
        logger.info(f"Task instruction {instruction}")
        if len(test_data_pd) == 0:
            logger.info("Not enough samples to run, continue to next task.")
            continue
        saved_funcs = []
        # remove previous demonstrations records from train_data_pd

        
        # we have a list of dataframes where each dataframe represent a task 
        saved_funcs, saved_vfuncs, saved_acc, generator, demonstrations, demon_df = function_generation(args, train_data_pd, instruction, task=task, llm=llm, lang=args.lang)
        print(demonstrations)
        all_saved_funcs.append(saved_funcs)
        batches = []
        test_data_lst = data_utils.deserialize_data(test_data_pd)
        batches = [test_data_lst]
        
        accs_per_batch = []
        gts_per_task = []
        preds_per_task = []
        invalid_data_per_batch = []
        i = 0
        logger.info(f"number of batches splitted is {len(batches)}")
        logger.info(f"number of funcs is {len(saved_funcs)}")

        # evaluate per batch
        if task in ["data_transformation", "error_detection_spelling"]:
            num_solution = None
            for batch, func, vfunc in zip(batches, saved_funcs, saved_vfuncs):
                logger.info(f"using function {func} to evaluate")
                
                # when there is no validation function, we route all data to the current function
                valid_data, invalid_data = generator.route_data(vfunc, batch)
                invalid_data_per_batch.append(invalid_data)
                acc, preds = generator.evaluate(func, valid_data)
               
                logger.info(f"acc: {acc} for batch {i}")
                accs_per_batch.append(acc)
                for sample, pred in zip(valid_data, preds):
                    gt = sample["Output"]
                    gts_per_task.append(gt)
                    preds_per_task.append(pred)
                    all_gts.append(gt)
                    all_preds.append(pred)
                    logger.info(f"====> pred: {pred} <====")
                    logger.info(f"====> gt: {gt} <====")

                if invalid_data:
                    for invalid_data_sample in invalid_data:
                        logger.info(f"====> invalid data: {invalid_data_sample} <====")
                    # run the fallback solution
                    if args.use_fallback:
                        logger.info("Using fallback solution.")
                        llmpr = LLMPR(model_name="gpt-4-turbo", task=task)
                        gts, preds = llmpr.pipeline(examples=demonstrations, test_data=invalid_data)
                        for gt, pred in zip(gts, preds):
                            gts_per_task.append(gt)
                            preds_per_task.append(pred)
                            all_gts.append(gt)
                            all_preds.append(pred)
                            logger.info(f"====> pred: {pred} <====")
                            logger.info(f"====> gt: {gt} <====")                   

        else:
            # for tasks entity matching and data imputation
            sorted_acc, sorted_funcs, sorted_vfuncs = zip(*sorted(zip(saved_acc, saved_funcs, saved_vfuncs), key=lambda x: x[0], reverse=True))
            func = sorted_funcs[0]
            vfunc = sorted_vfuncs[0]
            logger.info(f"sorted acc {sorted_acc}, sorted funcs {sorted_funcs}, sorted vfuncs {sorted_vfuncs}")
            logger.info(f"Acc for the fincal func is {sorted_acc[0]}, Final function to use is {func}, Final validation function to use is {vfunc}")           
            for batch in batches:
                valid_data, invalid_data = generator.route_data(vfunc, batch)
                invalid_data_per_batch.append(invalid_data)
                acc, preds = generator.evaluate(func, valid_data)
               
                logger.info(f"acc: {acc} for batch {i}")
                
                accs_per_batch.append(acc)
                for sample, pred in zip(valid_data, preds):
                    gt = sample["Output"]
                    gts_per_task.append(gt)
                    preds_per_task.append(pred)
                    all_gts.append(gt)
                    all_preds.append(pred)
                    logger.info(f"====> pred: {pred} <====")
                    logger.info(f"====> gt: {gt} <====")
                
                # single solution strategy
                # if invalid_data:
                #     for invalid_data_sample in invalid_data:
                #         logger.info(f"====> invalid data: {invalid_data_sample} <====")
                #     if not valid_data:
                #         logger.info("All data is invalid. We don't run the fallback solution.")
                #     else:
                #         # run the fallback solution
                #         # set up maximum number of invalid data to run the fallback solution 
                #         if args.use_fallback & len(invalid_data) < 100:
                #             logger.info("Using fallback solution.")
                #             llmpr = LLMPR(model_name="gpt-4-turbo", task=task)
                #             gts, preds = llmpr.pipeline(examples=demonstrations, test_data=invalid_data)
                #             for gt, pred in zip(gts, preds):
                #                 gts_per_task.append(gt)
                #                 preds_per_task.append(pred)
                #                 all_gts.append(gt)
                #                 all_preds.append(pred)
                #                 logger.info(f"====> pred: {pred} <====")
                #                 logger.info(f"====> gt: {gt} <====")  
                # 
                # Multiple solution strategy
                # the number of solutions should be determined by the length of invalid data in the future. 
                max_num_solutions = 5
                num_solution = 1
                while len(invalid_data) > limit_fallback:
                    logger.info(f"===========>Current number of solutions is {num_solution}<===========")
                    if num_solution >= max_num_solutions:
                        break
                    logger.info(f"length of invalid data is {len(invalid_data)}, generate new functions")
                    saved_funcs = []

                    # before regenerate another code solution, remove the previous demonstrations records from train_data_pd
                    train_data_pd = train_data_pd.drop(index=demon_df.index)
                    logger.info(f"length of train data after removing demonstrations is {train_data_pd.shape[0]}")
                    # we have a list of dataframes where each dataframe represent a task 
                    saved_funcs, saved_vfuncs, saved_acc, generator, demonstrations, demon_df = function_generation(args, train_data_pd, instruction, task=task, llm=llm, lang=args.lang)
                    sorted_acc, sorted_funcs, sorted_vfuncs = zip(*sorted(zip(saved_acc, saved_funcs, saved_vfuncs), key=lambda x: x[0], reverse=True))
                    func = sorted_funcs[0]
                    vfunc = sorted_vfuncs[0]
                    logger.info(f"sorted acc {sorted_acc}, sorted funcs {sorted_funcs}, sorted vfuncs {sorted_vfuncs}")
                    logger.info(f"Acc for the fincal func is {sorted_acc[0]}, Final function to use is {func}, Final validation function to use is {vfunc}")        
                    valid_data, invalid_data = generator.route_data(vfunc, invalid_data)
                    invalid_data_per_batch.append(invalid_data)
                    acc, preds = generator.evaluate(func, valid_data)
                    
                    logger.info(f"acc: {acc} for batch {i}")
                    
                    accs_per_batch.append(acc)
                    for sample, pred in zip(valid_data, preds):
                        gt = sample["Output"]
                        gts_per_task.append(gt)
                        preds_per_task.append(pred)
                        all_gts.append(gt)
                        all_preds.append(pred)
                        logger.info(f"====> pred: {pred} <====")
                        logger.info(f"====> gt: {gt} <====")
                    num_solution += 1



                if len(invalid_data) < limit_fallback:
                    logger.info(f"length of invalid data is {len(invalid_data)}, run the fallback solution")
                    logger.info("Using fallback solution.")
                    llmpr = LLMPR(model_name="gpt-4-turbo", task=task)
                    gts, preds = llmpr.pipeline(examples=demonstrations, test_data=invalid_data)
                    for gt, pred in zip(gts, preds):
                        gts_per_task.append(gt)
                        preds_per_task.append(pred)
                        all_gts.append(gt)
                        all_preds.append(pred)
                        logger.info(f"====> pred: {pred} <====")
                        logger.info(f"====> gt: {gt} <====")  
                
                else:
                    logger.info(f"Remaining invalid data size is {len(invalid_data)}. We don't run the fallback solution.")
                    for invalid_data_sample in invalid_data:
                        logger.info(f"====> invalid data: {invalid_data_sample} <====")

        logger.info(f"Number of solutions generated before running the fallback solution is {num_solution}")
        # calculating metrics per task
        prec, rec, acc, f1 = compute_metrics(preds_per_task, gts_per_task, task)
        logger.info(f"Task number {task_number}")
        logger.info(
            f"Prec: {prec:.3f} Recall: {rec:.3f} Acc: {acc:.3f} F1: {f1:.3f}"
        )
    
        task_metrics["rec"].append(rec)
        task_metrics["prec"].append(prec)
        task_metrics["acc"].append(acc)
        task_metrics["f1"].append(f1)


    output_file = (
        Path(args.output_dir)
        / f"{Path(args.data_dir).stem}"
        / f"{test_file}"
        / f"{args.k}k"
        / f"{args.d}d"
        f"_data_router_{int(args.use_data_router)}"
        f"_fallback_{int(args.use_fallback)}"
        f"_lang_{args.lang}"
        f"_llm_{llm}"
        f"_{int(args.class_balanced)}cb"
        f"_{args.sample_method}"
        f"_{args.num_run}run" / f"trial_{num_run}.feather"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saved to {output_file}")
    
    # calculate metrics all rows
    prec, rec, acc, f1 = compute_metrics(all_preds, all_gts, task=task)
    task_metrics["prec_on_rows"] = prec
    task_metrics["rec_on_rows"] = rec
    task_metrics["acc_on_rows"] = acc
    task_metrics["f1_on_rows"] = f1

    for k, values in list(task_metrics.items()):
        task_metrics[f"{k}_avg"] = np.average(values)
        task_metrics[f"{k}_std"] = np.std(values)

    output_metrics = output_file.parent / "metrics.json"
    json.dump(task_metrics, open(output_metrics, "w"))

    output_functions = output_file.parent / "learned_funcs.json"
    json.dump(all_saved_funcs, open(output_functions, "w"))
    logger.info(f"Final Metrics {json.dumps(task_metrics, indent=4)}")
    logger.info(f"Metrics dumped to {output_metrics}")
    logger.info(f"Learned funcs dumped to {output_functions}")



if __name__ == "__main__":
    main()