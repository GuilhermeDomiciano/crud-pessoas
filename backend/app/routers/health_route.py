from fastapi import APIRouter

from db.database import get_client

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
    return status
