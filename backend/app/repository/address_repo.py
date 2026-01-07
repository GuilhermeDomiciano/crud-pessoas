from bson import ObjectId
from fastapi import Depends
from pydantic import ValidationError
from pymongo import ReturnDocument

from db.database import get_db
from db.objectid import subdoc_to_public, to_object_id
from model.address import AddressBase, AddressInDB, AddressOut, AddressUpdate
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

    async def atualizar_endereco(
        self,
        person_id: str,
        address_id: str,
        address: AddressUpdate,
    ) -> AddressOut | None:
        obj_id = to_object_id(person_id)
        addr_id = to_object_id(address_id)
        data = address.model_dump(exclude_unset=True)
        set_ops = {f"addresses.$[addr].{key}": value for key, value in data.items()}
        set_ops["updatedAt"] = now_utc()
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": set_ops, "$inc": {"version": 1}},
            array_filters=[{"addr._id": addr_id}],
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            return None
        for address_doc in updated.get("addresses", []):
            if address_doc.get("_id") == addr_id:
                return self._to_public(address_doc)
        return None

    async def deletar_endereco(self, person_id: str, address_id: str) -> bool:
        obj_id = to_object_id(person_id)
        addr_id = to_object_id(address_id)
        existing = await self._collection.find_one(
            {"_id": obj_id, "deletedAt": None, "addresses._id": addr_id},
            {"addresses.$": 1},
        )
        if not existing:
            return False
        updated = await self._collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {
                "$pull": {"addresses": {"_id": addr_id}},
                "$set": {"updatedAt": now_utc()},
                "$inc": {"version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return updated is not None

def get_address_repository(db=Depends(get_db)) -> AddressRepository:
    return AddressRepository(db)
