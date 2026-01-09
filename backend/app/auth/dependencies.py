from __future__ import annotations

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from auth.api_key import is_valid_api_key
from auth.jwt import decode_jwt
from settings import settings


def _get_auth_mode() -> str:
    return (settings.auth_mode or "OFF").upper()


async def _require_api_key(x_api_key: str | None) -> dict:
    if not await is_valid_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
    return {"mode": "API_KEY", "scopes": []}


bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def _require_jwt(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    scopes = payload.get("scopes") or payload.get("roles") or []
    if isinstance(scopes, str):
        scopes = [scopes]
    return {
        "mode": "JWT",
        "sub": payload.get("sub"),
        "claims": payload,
        "scopes": scopes,
    }


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    x_api_key: str | None = Security(api_key_scheme),
) -> dict:
    mode = _get_auth_mode()
    if mode == "OFF":
        return {"mode": "OFF"}
    if mode == "API_KEY":
        return await _require_api_key(x_api_key)
    if mode == "JWT":
        return _require_jwt(credentials)
    if mode == "BOTH":
        if credentials:
            return _require_jwt(credentials)
        return await _require_api_key(x_api_key)
    raise HTTPException(status_code=500, detail="invalid auth mode")


def require_scopes(required: list[str]):
    async def _dependency(
        principal: dict = Depends(get_current_principal),
    ):
        mode = principal.get("mode")
        if mode in ("OFF", "API_KEY"):
            return principal
        scopes = principal.get("scopes") or []
        missing = [s for s in required if s not in scopes]
        if missing:
            raise HTTPException(status_code=403, detail="insufficient scope")
        return principal

    return _dependency


