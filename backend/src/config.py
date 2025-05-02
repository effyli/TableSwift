from pydantic_settings import BaseSettings
from pydantic import BaseModel
from functools import lru_cache
from fastapi_csrf_protect import CsrfProtect


class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database settings
    DB_FILE: str = "db/tableswift.db"
    
    # CSRF settings
    CSRF_SECRET_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()


class CsrfSettings(BaseModel):
    secret_key: str
    cookie_samesite: str = "lax"


@CsrfProtect.load_config
def get_csrf_config():
    settings = get_settings()
    return CsrfSettings(
        secret_key=settings.CSRF_SECRET_KEY,
    )