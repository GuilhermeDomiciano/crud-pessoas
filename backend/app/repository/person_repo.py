from datetime import date, datetime, timezone

from db.database import get_db
from db.objectid import doc_to_public, docs_to_public
from model.person import PersonCreate, PersonUpdate
from utils import now_utc
from db.objectid import to_object_id
from pymongo import ReturnDocument

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
    created = await db.person.find_one({"_id": result.inserted_id})
    return doc_to_public(created)

async def listar_pessoas(
    skip: int = 0,
    limit: int = 50,
    name: str | None = None,
    email: str | None = None,
):
    db = get_db()
    query: dict = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    cursor = db.person.find(query).skip(skip).limit(limit)
    persons = [person async for person in cursor]
    return docs_to_public(persons)

async def obter_pessoa(id: str):
    db = get_db()
    obj_id = to_object_id(id)
    person = await db.person.find_one({"_id": obj_id})
    return doc_to_public(person)

async def atualizar_pessoa(person_id: str, person_data: PersonUpdate):
    db = get_db()
    obj_id = to_object_id(person_id)
    data = person_data.model_dump(exclude_unset=True)
    birth_date = data.get("birth_date")
    if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
        data["birth_date"] = datetime(
            birth_date.year, birth_date.month, birth_date.day, tzinfo=timezone.utc
        )
    data["updated_at"] = now_utc()
    updated = await db.person.find_one_and_update(
        {"_id": obj_id},
        {"$set": data},
        return_document=ReturnDocument.AFTER,
    )
    return doc_to_public(updated)

async def deletar_pessoa(id: str):
    db = get_db()
    obj_id = to_object_id(id)
    deleted = await db.person.find_one_and_delete({"_id": obj_id})
    return doc_to_public(deleted)
