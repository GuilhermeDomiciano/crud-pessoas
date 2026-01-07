from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import (
    ensure_indexes,
    ensure_log_indexes,
    get_client,
    get_db,
    get_logs_db,
)
from middleware.request_logger import RequestLoggerMiddleware
from routers.addresses_route import router as address_router
from routers.health_route import router as health_router
from routers.persons_route import router as persons_router
from routers.phones_route import router as phones_router
from settings import settings

db = get_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes(db)
    await ensure_log_indexes(get_logs_db())
    yield
    get_client().close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(RequestLoggerMiddleware)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem vindo a minha API de CRUD de pessoas!"}


app.include_router(health_router)
app.include_router(persons_router)
app.include_router(address_router)
app.include_router(phones_router)
