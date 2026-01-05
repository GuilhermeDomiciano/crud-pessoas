from fastapi import FastAPI
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

app = FastAPI()

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

MONGODB_URI = os.getenv("MONGODB_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

@app.get("/health")
def ler_raiz():
    return {"Status": "Ok"}