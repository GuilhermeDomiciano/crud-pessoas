from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from auth.dependencies import require_scopes
from repository.dlq_repo import DlqRepository, get_dlq_repository
from repository.log_repo import LogRepository, get_log_repository
from services.dlq_service import DlqService
from services.log_service import LogService

router = APIRouter(tags=["logs"])


def get_log_service(
    repo: LogRepository = Depends(get_log_repository),
) -> LogService:
    return LogService(repo=repo)


def get_dlq_service(
    repo: DlqRepository = Depends(get_dlq_repository),
) -> DlqService:
    return DlqService(repo=repo)


@router.get("/logs/dlq")
async def listar_logs_dlq(
    limit: int = Query(50, ge=1, le=200),
    service: DlqService = Depends(get_dlq_service),
):
    return await service.listar_dlq(limit=limit)


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
    principal: dict = Depends(require_scopes(["persons:read"])),
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
