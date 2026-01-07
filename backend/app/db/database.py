from __future__ import annotations

import motor.motor_asyncio
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

def get_logs_db():
    return get_client()[settings.mongo_logs_db]


async def ensure_indexes(db) -> None:
    person = db["person"]

    await person.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="uniq_person_email",
    )

    await person.create_index(
        [("createdAt", DESCENDING)],
        name="idx_person_createdAt",
    )


async def ensure_log_indexes(db) -> None:
    logs = db["request_logs"]

    await logs.create_index(
        [("requestTime", DESCENDING)],
        name="idx_logs_requestTime",
    )

    await logs.create_index(
        [("statusCode", ASCENDING), ("requestTime", DESCENDING)],
        name="idx_logs_status_requestTime",
    )

    await logs.create_index(
        [("method", ASCENDING), ("url", ASCENDING), ("requestTime", DESCENDING)],
        name="idx_logs_method_url_requestTime",
    )

    ttl_days = settings.log_ttl_days
    if ttl_days and ttl_days > 0:
        await logs.create_index(
            [("requestTime", ASCENDING)],
            expireAfterSeconds=ttl_days * 86400,
            name="idx_logs_requestTime_ttl",
        )
