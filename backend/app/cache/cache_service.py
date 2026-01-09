from __future__ import annotations

import json
import logging
from typing import Any

from cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)


async def get_json(key: str) -> dict[str, Any] | list[Any] | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = await client.get(key)
    except Exception:
        logger.exception("Redis get failed", extra={"key": key})
        return None
    if raw is None:
        logger.info("cache_miss", extra={"key": key})
        return None
    logger.info("cache_hit", extra={"key": key})
    try:
        return json.loads(raw)
    except Exception:
        return None


async def set_json(key: str, value: Any, ttl: int | None) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        raw = json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
            default=str,
        )
        if ttl is None:
            await client.set(key, raw)
        else:
            await client.setex(key, ttl, raw)
        return True
    except Exception:
        logger.exception("Redis set failed", extra={"key": key})
        return False


async def delete(key: str) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        await client.delete(key)
        return True
    except Exception:
        logger.exception("Redis delete failed", extra={"key": key})
        return False


async def incr(key: str) -> int | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        return int(await client.incr(key))
    except Exception:
        logger.exception("Redis incr failed", extra={"key": key})
        return None
