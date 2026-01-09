from __future__ import annotations

from redis import asyncio as redis

from settings import settings

_client: redis.Redis | None = None


async def init_redis() -> None:
    global _client
    if _client is not None or not settings.redis_url:
        return
    _client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await _client.ping()
    except Exception:
        _client = None


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.close()
    _client = None


def get_redis_client() -> redis.Redis | None:
    return _client


async def ping_redis() -> bool:
    if not settings.redis_url:
        return False
    if _client is not None:
        try:
            return bool(await _client.ping())
        except Exception:
            return False
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        ok = await client.ping()
        await client.close()
        return bool(ok)
    except Exception:
        return False
