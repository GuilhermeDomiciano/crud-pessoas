from datetime import UTC, date, datetime

from bson import ObjectId
from fastapi import Depends
from pydantic import ValidationError
from pymongo import ReturnDocument

from db.database import get_db
from db.objectid import doc_to_public, to_object_id
from model.person import PersonCreate, PersonInDB, PersonUpdate
from utils import now_utc


class PersonRepository:
    def __init__(self, db):
        self._collection = db.person

    @staticmethod
    def _to_public(doc):
        if doc is None:
            return None
        try:
            validated = PersonInDB.model_validate(doc).model_dump(by_alias=True)
        except ValidationError:
            return None
        return doc_to_public(validated)

    @staticmethod
    def _ensure_subdoc_ids(items):
        if not items:
            return []
        updated = []
        for item in items:
            if "_id" not in item or item["_id"] is None:
                item["_id"] = ObjectId()
            elif isinstance(item["_id"], str):
                item["_id"] = to_object_id(item["_id"])
            updated.append(item)
        return updated

    async def criar_pessoa(self, person: PersonCreate):
        data = person.model_dump(by_alias=True)
        date_of_birth = data.get("dateOfBirth")
        if isinstance(date_of_birth, date) and not isinstance(date_of_birth, datetime):
            data["dateOfBirth"] = datetime(
                date_of_birth.year, date_of_birth.month, date_of_birth.day, tzinfo=UTC
            )
        data["addresses"] = self._ensure_subdoc_ids(data.get("addresses"))
        data["phoneNumbers"] = self._ensure_subdoc_ids(data.get("phoneNumbers"))
        now = now_utc()
        data["createdAt"] = now
        data["updatedAt"] = now
        data["version"] = 1
        data["deletedAt"] = None
        result = await self._collection.insert_one(data)
        created = await self._collection.find_one({"_id": result.inserted_id})
        return self._to_public(created)

    async def listar_pessoas(
        self,
        skip: int = 0,
        limit: int = 50,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ):
        query: dict = {"deletedAt": None}
        if first_name:
            query["firstName"] = {"$regex": first_name, "$options": "i"}
        if last_name:
            query["lastName"] = {"$regex": last_name, "$options": "i"}
        if email:
            query["email"] = {"$regex": email, "$options": "i"}
        cursor = self._collection.find(query).skip(skip).limit(limit)
        persons = []
        async for person in cursor:
            public = self._to_public(person)
            if public is not None:
                persons.append(public)
        return persons

    async def obter_pessoa(self, id: str):
        obj_id = to_object_id(id)
        person = await self._collection.find_one({"_id": obj_id, "deletedAt": None})
        return self._to_public(person)

    async def atualizar_pessoa(self, person_id: str, person_data: PersonUpdate):
        obj_id = to_object_id(person_id)
        data = person_data.model_dump(exclude_unset=True, by_alias=True)
        date_of_birth = data.get("dateOfBirth")
        if isinstance(date_of_birth, date) and not isinstance(date_of_birth, datetime):
            data["dateOfBirth"] = datetime(
                date_of_birth.year, date_of_birth.month, date_of_birth.day, tzinfo=UTC
            )
        if "addresses" in data:
            data["addresses"] = self._ensure_subdoc_ids(data["addresses"])
        if "phoneNumbers" in data:
            data["phoneNumbers"] = self._ensure_subdoc_ids(data["phoneNumbers"])
        data["updatedAt"] = now_utc()
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": data, "$inc": {"version": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_public(updated)

    async def deletar_pessoa(self, id: str):
        obj_id = to_object_id(id)
        deleted = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": {"deletedAt": now_utc(), "updatedAt": now_utc()}, "$inc": {"version": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_public(deleted)


def get_person_repository(db=Depends(get_db)) -> PersonRepository:
    return PersonRepository(db)
