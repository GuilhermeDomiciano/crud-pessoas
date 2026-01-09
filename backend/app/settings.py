from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    app_name: str = "CRUD Pessoas"
    env: str = "dev"

    mongo_uri: str = Field(validation_alias="MONGODB_URI")
    mongo_db: str = Field(default="personal_db", validation_alias="MONGODB_DB")
    mongo_logs_db: str = Field(default="app_logs", validation_alias="MONGODB_LOGS_DB")
    log_ttl_days: int = Field(default=30, validation_alias="LOG_TTL_DAYS")
    log_body_max_bytes: int = Field(default=10_240, validation_alias="LOG_BODY_MAX_BYTES")

    rabbitmq_url: str | None = Field(default=None, validation_alias="RABBITMQ_URL")
    logger: str = Field(default="ON", validation_alias="LOGGER")
    logger_mode: str = Field(default="ASYNC", validation_alias="LOGGER_MODE")

    redis_url: str | None = Field(default=None, validation_alias="REDIS_URL")
    cache: str = Field(default="OFF", validation_alias="CACHE")
    cache_ttl_person_seconds: int = Field(
        default=300,
        validation_alias="CACHE_TTL_PERSON_SECONDS",
    )
    cache_ttl_list_seconds: int = Field(
        default=60,
        validation_alias="CACHE_TTL_LIST_SECONDS",
    )

    auth_mode: str = Field(default="OFF", validation_alias="AUTH_MODE")
    jwt_secret: str | None = Field(default=None, validation_alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", validation_alias="JWT_ALG")
    jwt_expires_min: int = Field(default=60, validation_alias="JWT_EXPIRES_MIN")
    api_keys: str | None = Field(default=None, validation_alias="API_KEYS")
    auth_user: str | None = Field(default=None, validation_alias="AUTH_USER")
    auth_password: str | None = Field(default=None, validation_alias="AUTH_PASSWORD")
    auth_roles: str | None = Field(default=None, validation_alias="AUTH_ROLES")


settings = Settings()
