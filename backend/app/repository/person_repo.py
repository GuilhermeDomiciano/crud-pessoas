from datetime import date, datetime, timezone

from db.database import get_db
from model.person import PersonCreate
from utils import now_utc


async def criar_pessoa(person: PersonCreate):
    db = get_db()
    data = person.model_dump()
    birth_date = data.get("birth_date")
    if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
        data["birth_date"] = datetime(
            birth_date.year, birth_date.month, birth_date.day, tzinfo=timezone.utc
        )
    now = now_utc()
    data["created_at"] = now
    data["updated_at"] = now
    result = await db.person.insert_one(data)
    return result.inserted_id