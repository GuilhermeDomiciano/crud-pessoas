from fastapi import APIRouter

from cache.redis_client import ping_redis
from db.database import get_client
from messaging.rabbitmq import ping_rabbitmq
from settings import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health():
    return {"status": "ok"}


@router.get("/ping")
async def ping():
    status = {"status": "ok"}
    try:
        await get_client().admin.command("ping")
        status["db"] = "ok"
    except Exception:
        status["db"] = "error"
    if not settings.redis_url:
        status["redis"] = "disabled"
    else:
        status["redis"] = "ok" if await ping_redis() else "error"
    if not settings.rabbitmq_url:
        status["rabbitmq"] = "disabled"
    else:
        status["rabbitmq"] = "ok" if await ping_rabbitmq() else "error"
    return status


@router.get("/rabbit")
async def rabbit():
    if not settings.rabbitmq_url:
        return {"rabbitmq": "disabled"}
    return {"rabbitmq": "ok" if await ping_rabbitmq() else "error"}

