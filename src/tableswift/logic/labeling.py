from typing import List
from ..llm_pr.llmpr import LLMPR


def label_data_logic(instruction: str, column_name: str, task:str, demonstrations: List[dict],
                      samples_to_label: List[dict], api_key: str, hyperparams: dict) -> List[str]:
    """
    Generate labels for the input samples based on the provided instruction.
    """
    print("Labeling data logic...")
    print(f"Instruction: {instruction}")
    print(f"Task: {task}")
    print(f"Column Name: {column_name}")
    print(f"demonstration: {demonstrations}")

    llm = hyperparams["llm"]
    
    # Here we would typically call an LLM to generate labels based on the instruction and input samples
    # use llmpr to generate labels
    llm_pr = LLMPR(task=task, api_key=api_key, model_name=llm)
    transformed_samples = llm_pr.pipeline_no_eval(instruction, column_name, demonstrations, samples_to_label)
    return transformed_samples