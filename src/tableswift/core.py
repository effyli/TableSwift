from typing import List
from .config import with_api_key, resolve_hyperparams
from .logic.codegen import generate_code_logic


@with_api_key
def generate_labels(instruction: str, input_samples: List[str],api_key=None, **overrides) -> None:
    """
    Generate labels given instructions and input samples.
    """
    
    return None

@with_api_key
def generate_code(instruction: str, task:str, samples: List[List], lang: str, api_key=None, **overrides) -> str:
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

def execute_code(code: str, inputs: List[str]) -> None:
    """
    Execute the generated code.
    """
    return None

