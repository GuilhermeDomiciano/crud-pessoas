from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    requestTime: datetime
    responseTime: datetime
    method: str
    url: str
    statusCode: int
    userAgent: str | None = None
    body: dict[str, Any] | list[Any] | str | None = None
    params: dict[str, Any] | None = None
    query: dict[str, Any] | None = None
    durationMs: float | None = None
    requestId: str | None = None
    ip: str | None = None
    logVersion: int | None = Field(default=None, alias="__v")
