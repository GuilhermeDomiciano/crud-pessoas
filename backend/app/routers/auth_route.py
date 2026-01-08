from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.jwt import encode_jwt
from settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
async def emitir_token(payload: TokenRequest):
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="jwt secret not configured")
    if not settings.auth_user or not settings.auth_password:
        raise HTTPException(status_code=500, detail="auth credentials not configured")
    if payload.username != settings.auth_user or payload.password != settings.auth_password:
        raise HTTPException(status_code=401, detail="invalid credentials")

    roles = []
    if settings.auth_roles:
        roles = [r.strip() for r in settings.auth_roles.split(",") if r.strip()]
    extra = {"roles": roles} if roles else None
    token = encode_jwt(subject=settings.auth_user, extra=extra)
    return {"access_token": token, "token_type": "bearer"}
