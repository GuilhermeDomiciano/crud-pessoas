from __future__ import annotations

from redis import asyncio as redis

from settings import settings

_client: redis.Redis | None = None
def _timeout_seconds() -> float:
    return max(0.05, settings.redis_timeout_ms / 1000)


async def init_redis() -> None:
    global _client
    if _client is not None or not settings.redis_url:
        return
    timeout = _timeout_seconds()
    _client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=timeout,
        socket_timeout=timeout,
    )
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
        timeout = _timeout_seconds()
        client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
        )
        ok = await client.ping()
        await client.close()
        return bool(ok)
    except Exception:
        return False
