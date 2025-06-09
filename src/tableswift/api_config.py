# config file for setting up API keys for Tableswift

import os

_api_key = None

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