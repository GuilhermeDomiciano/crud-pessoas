from contextlib import asynccontextmanager
from fastapi import FastAPI
from settings import settings
from db.database import get_db, get_client, ensure_indexes
from routers.health_route import router as health_router
from routers.persons_route import router as persons_router

db = get_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes(db)
    yield
    get_client().close()
    
app = FastAPI(title=settings.app_name, lifespan=lifespan)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem vindo a minha API de CRUD de pessoas!"}

app.include_router(health_router)
app.include_router(persons_router)