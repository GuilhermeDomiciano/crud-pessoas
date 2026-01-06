from bson import ObjectId
from fastapi import Depends
from pydantic import ValidationError
from pymongo import ReturnDocument

from db.database import get_db
from db.objectid import subdoc_to_public, to_object_id
from model.address import AddressBase, AddressInDB, AddressOut
from utils import now_utc


class AddressRepository:
    def __init__(self, db):
        self._collection = db.person

    @staticmethod
    def _to_public(doc):
        if doc is None:
            return None
        try:
            validated = AddressInDB.model_validate(doc).model_dump(by_alias=True)
        except ValidationError:
            return None
        return subdoc_to_public(validated)

    async def criar_enderecos(
        self,
        id_person: str,
        addresses: list[AddressBase],
    ) -> list[AddressOut] | None:
        if not addresses:
            return []
        address_dicts = []
        for address in addresses:
            address_dict = address.model_dump()
            address_dict["_id"] = ObjectId()
            address_dicts.append(address_dict)
        obj_id = to_object_id(id_person)
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {
                "$push": {"addresses": {"$each": address_dicts}},
                "$set": {"updatedAt": now_utc()},
                "$inc": {"version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        if not updated or "addresses" not in updated or not updated["addresses"]:
            return None
        new_address_docs = updated["addresses"][-len(address_dicts):]
        results = []
        for address_doc in new_address_docs:
            public = self._to_public(address_doc)
            if public is not None:
                results.append(public)
        return results

def get_address_repository(db=Depends(get_db)) -> AddressRepository:
    return AddressRepository(db)
