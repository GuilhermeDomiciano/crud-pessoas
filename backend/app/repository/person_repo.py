from datetime import date, datetime, timezone

from fastapi import Depends
from pymongo import ReturnDocument

from db.database import get_db
from db.objectid import doc_to_public, docs_to_public, to_object_id
from model.person import PersonCreate, PersonUpdate
from utils import now_utc


class PersonRepository:
    def __init__(self, db):
        self._collection = db.person

    async def criar_pessoa(self, person: PersonCreate):
        data = person.model_dump()
        birth_date = data.get("birth_date")
        if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
            data["birth_date"] = datetime(
                birth_date.year, birth_date.month, birth_date.day, tzinfo=timezone.utc
            )
        now = now_utc()
        data["created_at"] = now
        data["updated_at"] = now
        result = await self._collection.insert_one(data)
        created = await self._collection.find_one({"_id": result.inserted_id})
        return doc_to_public(created)

    async def listar_pessoas(
        self,
        skip: int = 0,
        limit: int = 50,
        name: str | None = None,
        email: str | None = None,
    ):
        query: dict = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if email:
            query["email"] = {"$regex": email, "$options": "i"}
        cursor = self._collection.find(query).skip(skip).limit(limit)
        persons = [person async for person in cursor]
        return docs_to_public(persons)

    async def obter_pessoa(self, id: str):
        obj_id = to_object_id(id)
        person = await self._collection.find_one({"_id": obj_id})
        return doc_to_public(person)

    async def atualizar_pessoa(self, person_id: str, person_data: PersonUpdate):
        obj_id = to_object_id(person_id)
        data = person_data.model_dump(exclude_unset=True)
        birth_date = data.get("birth_date")
        if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
            data["birth_date"] = datetime(
                birth_date.year, birth_date.month, birth_date.day, tzinfo=timezone.utc
            )
        data["updated_at"] = now_utc()
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return doc_to_public(updated)

    async def deletar_pessoa(self, id: str):
        obj_id = to_object_id(id)
        deleted = await self._collection.find_one_and_delete({"_id": obj_id})
        return doc_to_public(deleted)


def get_person_repository(db=Depends(get_db)) -> PersonRepository:
    return PersonRepository(db)
