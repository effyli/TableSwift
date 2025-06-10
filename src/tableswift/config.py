# config file for setting up API keys for Tableswift

import os

_api_key = None
_params = {}
# Default parameters for the Tableswift API, can be overridden by user
DEFAULT_PARAMS = {
    "use_data_router": True,
    "num_trials": 2,
    "num_retry": 3,
    "seed": 42,
    "num_iterations": 2,
    "max_num_solutions": 3,
    "limit_fallback": 20, # number of invalid data samples before fallback, should be a percentage in the future
    "llm": "gpt-4o-mini" 
}

def configure(api_key: str):
    global _api_key
    _api_key = api_key

def get_api_key():
    return _api_key or os.getenv("TABLESWIFT_API_KEY")

def require_api_key():
    key = get_api_key()
    if not key:
        raise ValueError("No API key provided. Use configure() or set TABLESWIFT_API_KEY env var.")
    return key

def with_api_key(func):
    def wrapper(*args, **kwargs):
        key = require_api_key()
        return func(*args, api_key=key, **kwargs)
    return wrapper

def get_param(name):
    return _params.get(name, DEFAULT_PARAMS.get(name))

def resolve_hyperparams(overrides: dict = None):
    overrides = overrides or {}
    params = {}

    for param_name in DEFAULT_PARAMS:
        params[param_name] = overrides.get(
            param_name, 
            get_param(param_name)
        )

    return params