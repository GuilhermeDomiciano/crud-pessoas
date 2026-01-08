from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogError(BaseModel):
    code: int | None = None
    message: str | None = None


class RequestLog(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    requestTime: datetime
    responseTime: datetime
    method: str
    url: str
    statusCode: int
    userAgent: str | None = None
    headers: dict[str, str] | None = None
    body: dict[str, Any] | list[Any] | str | None = None
    params: dict[str, Any] | None = None
    query: dict[str, Any] | None = None
    durationMs: float | None = None
    ip: str | None = None
    requestId: str | None = None
    error: LogError | None = None
    logVersion: int | None = Field(default=None, alias="__v")
