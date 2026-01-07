from __future__ import annotations

import json
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from db.database import get_logs_db
from log_utils import extract_error, mask_sensitive, truncate_body
from settings import settings
from utils import now_utc


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

        response_body = None
        if response.status_code >= 400:
            try:
                if getattr(response, "body", None) is not None:
                    raw = response.body
                    if raw:
                        try:
                            response_body = json.loads(raw.decode("utf-8"))
                        except Exception:
                            response_body = raw.decode("utf-8", errors="ignore")
            except Exception:
                response_body = None

        error = extract_error(response.status_code, response_body)
        masked_body = mask_sensitive(body_obj) if body_obj is not None else None
        truncated_body, _truncated, _size = truncate_body(
            masked_body,
            settings.log_body_max_bytes,
        )

        log_doc = {
            "requestTime": request_time,
            "responseTime": response_time,
            "method": request.method,
            "url": url,
            "statusCode": response.status_code,
            "userAgent": request.headers.get("user-agent"),
            "body": truncated_body,
            "params": request.path_params or None,
            "query": dict(request.query_params) or None,
            "durationMs": duration_ms,
            "ip": request.client.host if request.client else None,
            "requestId": request_id,
            "error": error,
            "__v": 1,
        }

        try:
            logs_db = get_logs_db()
            await logs_db["request_logs"].insert_one(log_doc)
        except Exception:
            pass

        return response
