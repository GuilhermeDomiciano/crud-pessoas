from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from settings import settings


def encode_jwt(subject: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    if not settings.jwt_secret:
        raise ValueError("JWT_SECRET is not configured")
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_min)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_jwt(token: str) -> dict[str, Any]:
    if not settings.jwt_secret:
        raise ValueError("JWT_SECRET is not configured")
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])


