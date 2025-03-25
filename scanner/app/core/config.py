import os
from functools import lru_cache

from pydantic import BaseSettings, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Scanner"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_VERSION: str = os.environ.get("API_VERSION", "v1")
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    HASHING_ALGORITHM: str = os.environ.get("HASHING_ALGORITHM")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    USER_TABLE: str = os.environ.get("USER_TABLE")

    @field_validator(
        "DATABASE_URL", "HASHING_ALGORITHM", "SECRET_KEY", "USER_TABLE", mode="before"
    )
    def validate_required_fields(cls, value, field):
        if not value:
            raise ValueError(f"{field.name} is not set")
        return value

    class Config:
        env_file = "dev.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()


settings = get_settings()
