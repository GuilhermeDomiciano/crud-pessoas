from __future__ import annotations

import json
import logging
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from db.database import get_logs_db
from log_utils import mask_sensitive, truncate_body
from messaging.rabbitmq import publish_log_message
from model.log_message import LogMessage
from settings import settings
from utils import now_utc

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_time = now_utc()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        body_obj = None
        try:
            body_bytes = await request.body()
            if body_bytes:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body_obj = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            body_obj = None

        response = await call_next(request)

        response_time = now_utc()
        duration_ms = (response_time - request_time).total_seconds() * 1000
        route = request.scope.get("route")
        url = route.path if route and hasattr(route, "path") else request.url.path

        masked_body = mask_sensitive(body_obj) if body_obj is not None else None
        truncated_body, _truncated, _size = truncate_body(
            masked_body,
            settings.log_body_max_bytes,
        )
        log_message = LogMessage(
            requestTime=request_time,
            responseTime=response_time,
            method=request.method,
            url=url,
            statusCode=response.status_code,
            userAgent=request.headers.get("user-agent"),
            body=truncated_body,
            params=request.path_params or None,
            query=dict(request.query_params) or None,
            durationMs=duration_ms,
            ip=request.client.host if request.client else None,
            requestId=request_id,
            logVersion=1,
        )
        log_doc = log_message.model_dump(by_alias=True, exclude_none=True)

        if settings.logger.upper() != "ON":
            return response

        mode = settings.logger_mode.upper()
        if mode == "DISABLE":
            return response

        if mode == "SYNC":
            try:
                logs_db = get_logs_db()
                await logs_db["request_logs"].insert_one(log_doc)
            except Exception:
                logger.exception("Failed to write log to MongoDB")
            return response

        try:
            await publish_log_message(log_doc)
        except Exception:
            try:
                logger.error(
                    "Failed to publish log message, payload=%s",
                    json.dumps(log_doc, ensure_ascii=True, separators=(",", ":")),
                )
            except Exception:
                logger.exception("Failed to publish log message")

        return response
