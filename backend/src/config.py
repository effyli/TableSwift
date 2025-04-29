from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database settings
    DB_FILE: str = "db/tableswift.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
