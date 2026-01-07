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


settings = Settings()
