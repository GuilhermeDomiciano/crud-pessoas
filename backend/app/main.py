from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from cache.redis_client import close_redis, init_redis
from db.database import (
    ensure_indexes,
    ensure_log_indexes,
    get_client,
    get_db,
    get_logs_db,
)
from messaging.rabbitmq import close_rabbitmq, init_rabbitmq
from middleware.request_logger import RequestLoggerMiddleware
from routers.addresses_route import router as address_router
from routers.auth_route import router as auth_router
from routers.health_route import router as health_router
from routers.logs_route import router as logs_router
from routers.persons_route import router as persons_router
from routers.phones_route import router as phones_router
from settings import settings

db = get_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes(db)
    await ensure_log_indexes(get_logs_db())
    await init_redis()
    await init_rabbitmq()
    yield
    get_client().close()
    await close_redis()
    await close_rabbitmq()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(RequestLoggerMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"error": {"code": 401, "message": "unauthorized"}},
        )
    if exc.status_code == 403:
        return JSONResponse(
            status_code=403,
            content={"error": {"code": 403, "message": "forbidden"}},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem vindo a minha API de CRUD de pessoas!"}


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(persons_router)
app.include_router(address_router)
app.include_router(phones_router)
app.include_router(logs_router)


