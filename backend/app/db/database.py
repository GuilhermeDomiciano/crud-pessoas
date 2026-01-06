from __future__ import annotations

from dotenv import load_dotenv
from pathlib import Path
import motor.motor_asyncio
import os
from pymongo import ASCENDING, DESCENDING
from settings import settings

_client: motor.motor_asyncio.AsyncIoMotorClient | None = None

def get_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = settings.mongo_uri
        if not uri:
            raise RuntimeError("MONGODB_URI não está definido no .env")
        _client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    return _client

def get_db():
    return get_client()[settings.mongo_db]

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
