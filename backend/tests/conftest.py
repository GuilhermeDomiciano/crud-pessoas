import importlib
import os
import sys
import uuid
from pathlib import Path

import httpx
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
sys.path.insert(0, str(APP_DIR))

TEST_DB_NAME = f"test_persons_{uuid.uuid4().hex}"
os.environ["MONGODB_DB"] = TEST_DB_NAME

from db.database import ensure_indexes, get_client, get_db


@pytest.fixture(scope="module")
def app():
    main = importlib.import_module("main")
    return main.app


@pytest.fixture(scope="module")
async def initialized_db():
    db = get_db()
    await ensure_indexes(db)
    yield db
    client = get_client()
    await client.drop_database(db.name)
    client.close()


@pytest.fixture(autouse=True)
async def cleanup_db(initialized_db):
    await initialized_db.person.delete_many({})
    yield


@pytest.fixture
async def client(app, initialized_db):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
