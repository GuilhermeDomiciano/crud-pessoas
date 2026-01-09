from __future__ import annotations

import hashlib
import hmac

from db.database import get_db
from settings import settings


def _parse_keys(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


async def _is_valid_api_key_db(key: str) -> bool:
    key_hash = _hash_key(key)
    db = get_db()
    doc = await db["api_keys"].find_one(
        {"keyHash": key_hash, "status": "active"},
        {"keyHash": 1},
    )
    if not doc or "keyHash" not in doc:
        return False
    return hmac.compare_digest(key_hash, doc["keyHash"])


def _is_valid_api_key_env(key: str) -> bool:
    keys = _parse_keys(settings.api_keys)
    return any(hmac.compare_digest(key, stored) for stored in keys)


async def is_valid_api_key(key: str | None) -> bool:
    if not key:
        return False
    if settings.api_keys:
        return _is_valid_api_key_env(key)
    return await _is_valid_api_key_db(key)


