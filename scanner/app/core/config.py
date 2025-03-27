import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Scanner"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    TOKEN_REFRESH_THRESHOLD_PERCENT: float = 0.1  # 10% of the total lifetime
    TOKEN_TABLE: str = os.environ.get("TOKEN_TABLE")
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
            raise ValueError(f"{field} is not set")
        return value

    class Config:
        env_file = "dev.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
