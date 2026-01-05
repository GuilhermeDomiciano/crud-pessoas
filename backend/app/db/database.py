from __future__ import annotations

from dotenv import load_dotenv
from pathlib import Path
import motor.motor_asyncio
import os
from pymongo import ASCENDING, DESCENDING

_client: motor.motor_asyncio.AsyncIoMotorClient | None = None

def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=env_path)

def get_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    global _client
    if _client is None:
        _load_env()
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI não está definido no .env")
        _client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    return _client

def get_db():
    _load_env()
    db_name = os.getenv("MONGO_DB", "personal_db")
    return get_client()[db_name]

async def ensure_indexes(db) -> None:
    person = db["person"]

    await person.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="uniq_person_email",
    )
    
    await person.create_index(
        [("created_at", DESCENDING)],
        name="idx_person_created_at",
    )
