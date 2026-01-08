from __future__ import annotations

from fastapi import Header, HTTPException
from jwt import InvalidTokenError

from auth.api_key import is_valid_api_key
from auth.jwt import decode_jwt
from settings import settings


def _get_auth_mode() -> str:
    return (settings.auth_mode or "OFF").upper()


def _require_api_key(x_api_key: str | None) -> dict:
    if not is_valid_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
    return {"mode": "API_KEY"}


def _require_jwt(authorization: str | None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_jwt(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    return {"mode": "JWT", "sub": payload.get("sub"), "claims": payload}


def get_current_principal(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    mode = _get_auth_mode()
    if mode == "OFF":
        return {"mode": "OFF"}
    if mode == "API_KEY":
        return _require_api_key(x_api_key)
    if mode == "JWT":
        return _require_jwt(authorization)
    if mode == "BOTH":
        if authorization:
            return _require_jwt(authorization)
        return _require_api_key(x_api_key)
    raise HTTPException(status_code=500, detail="invalid auth mode")
