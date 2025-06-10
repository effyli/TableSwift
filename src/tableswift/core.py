from typing import List
from .config import with_api_key, resolve_hyperparams
from .logic.codegen import generate_code_logic
from .logic.execution import execute_code_logic
from .logic.labeling import label_data_logic


@with_api_key
def generate_labels(instruction: str, task: str, samples_to_label: List, column_name: str, api_key=None, demonstrations: List[dict]=None, **overrides) -> None:
    """
    Generate labels given instructions and input samples.
    """
    # input should be a list of dictionaries
    hyperparams = resolve_hyperparams(overrides)
    return label_data_logic(
        instruction=instruction,
        column_name=column_name,
        task=task,
        demonstrations=demonstrations,
        samples_to_label=samples_to_label,
        api_key=api_key, 
        hyperparams=hyperparams)

@with_api_key
def generate_code(instruction: str, task:str, samples: List, lang: str, api_key=None, **overrides) -> str:
    """
    Generate code given instructions and input samples.
    """
    hyperparams = resolve_hyperparams(overrides)
    return generate_code_logic(
        lang=lang,
        task=task,
        instruction=instruction,
        samples=samples,
        api_key=api_key,
        hyperparams=hyperparams
    )

@with_api_key
def execute_code(code: str, task: str, lang: str, instruction: str, inputs: List, samples: List,
                 router_code: str=None, api_key: str=None, **overrides) -> None:
    """
    Execute the generated code.
    """
    hyperparams = resolve_hyperparams(overrides)
    return execute_code_logic(
        code=code,
        lang=lang,
        router_code=router_code,
        instruction=instruction,
        inputs=inputs,
        demonstrations=samples,
        task=task,
        hyperparams=hyperparams,
        api_key=api_key)

