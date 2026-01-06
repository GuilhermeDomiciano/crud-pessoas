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
    
settings = Settings()
