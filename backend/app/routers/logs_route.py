from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from repository.log_repo import LogRepository, get_log_repository
from services.log_service import LogService

router = APIRouter(tags=["logs"])


def get_log_service(
    repo: LogRepository = Depends(get_log_repository),
) -> LogService:
    return LogService(repo=repo)


@router.get("/logs")
async def listar_logs(
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = None,
    statusCode: int | None = None,
    method: str | None = None,
    url: str | None = None,
    eventType: str | None = None,
    service: LogService = Depends(get_log_service),
):
    return await service.listar_logs(
        limit=limit,
        cursor=cursor,
        status_code=statusCode,
        method=method,
        url=url,
        event_type=eventType,
    )


@router.get("/persons/{id}/logs")
async def listar_logs_pessoa(
    id: str,
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = None,
    statusCode: int | None = None,
    method: str | None = None,
    url: str | None = None,
    eventType: str | None = None,
    service: LogService = Depends(get_log_service),
):
    return await service.listar_logs(
        limit=limit,
        cursor=cursor,
        status_code=statusCode,
        method=method,
        url=url,
        event_type=eventType,
        person_id=id,
    )
