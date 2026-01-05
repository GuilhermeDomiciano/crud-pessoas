from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import get_db, get_client, ensure_indexes

db = get_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes(db)
    yield
    get_client().close()
    
app = FastAPI(lifespan=lifespan)


@app.get("/health")
def ler_raiz():
    return {"Status": "Ok"}


@app.get("/ping")
async def ping():
    result = await db.command("ping")
    return result
    
