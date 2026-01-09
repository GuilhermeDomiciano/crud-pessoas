from bson import ObjectId
from fastapi import Depends
from pydantic import ValidationError
from pymongo import ReturnDocument

from db.database import get_db
from db.objectid import subdoc_to_public, to_object_id
from model.phone import PhoneBase, PhoneInDB, PhoneOut, PhoneUpdate
from utils import now_utc


class PhoneRepository:
    def __init__(self, db):
        self._collection = db.person

    @staticmethod
    def _to_public(doc):
        if doc is None:
            return None
        try:
            validated = PhoneInDB.model_validate(doc).model_dump(by_alias=True)
        except ValidationError:
            return None
        return subdoc_to_public(validated)

    async def criar_telefones(
        self,
        id_person: str,
        phones: list[PhoneBase],
    ) -> list[PhoneOut] | None:
        if not phones:
            return []
        phone_dicts = []
        for phone in phones:
            phone_dict = phone.model_dump()
            phone_dict["_id"] = ObjectId()
            phone_dicts.append(phone_dict)
        obj_id = to_object_id(id_person)
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {
                "$push": {"phoneNumbers": {"$each": phone_dicts}},
                "$set": {"updatedAt": now_utc()},
                "$inc": {"version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        if not updated or "phoneNumbers" not in updated or not updated["phoneNumbers"]:
            return None
        new_phone_docs = updated["phoneNumbers"][-len(phone_dicts):]
        results = []
        for phone_doc in new_phone_docs:
            public = self._to_public(phone_doc)
            if public is not None:
                results.append(public)
        return results

    async def atualizar_telefone(
        self,
        person_id: str,
        phone_id: str,
        phone: PhoneUpdate,
    ) -> PhoneOut | None:
        obj_id = to_object_id(person_id)
        phone_id = to_object_id(phone_id)
        data = phone.model_dump(exclude_unset=True)
        set_ops = {f"phoneNumbers.$[phon].{key}": value for key, value in data.items()}
        set_ops["updatedAt"] = now_utc()
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": set_ops, "$inc": {"version": 1}},
            array_filters=[{"phon._id": phone_id}],
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            return None
        for phone_doc in updated.get("phoneNumbers", []):
            if phone_doc.get("_id") == phone_id:
                return self._to_public(phone_doc)
        return None

    async def deletar_telefone(self, person_id: str, phone_id: str) -> bool:
        obj_id = to_object_id(person_id)
        phone_id = to_object_id(phone_id)
        existing = await self._collection.find_one(
            {"_id": obj_id, "deletedAt": None, "phoneNumbers._id": phone_id},
            {"phoneNumbers.$": 1},
        )
        if not existing:
            return False
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {
                "$pull": {"phoneNumbers": {"_id": phone_id}},
                "$set": {"updatedAt": now_utc()},
                "$inc": {"version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return updated is not None

def get_phone_repository(db=Depends(get_db)) -> PhoneRepository:
    return PhoneRepository(db)


