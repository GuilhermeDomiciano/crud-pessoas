from fastapi import FastAPI

from db.database import db_client


app = FastAPI()
client = db_client()
db = client["test_database"]


@app.get("/health")
def ler_raiz():
    return {"Status": "Ok"}


@app.get("/ping")
async def ping():
    result = await db.command("ping")
    return result
    
