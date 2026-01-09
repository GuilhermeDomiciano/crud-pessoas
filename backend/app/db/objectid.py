from __future__ import annotations

from typing import Any

from bson import ObjectId


def to_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise ValueError("id inválido")
    return ObjectId(id_str)


def doc_to_public(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if doc is None:
        return None
    for key in ("addresses", "phoneNumbers"):
        items = doc.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and "_id" in item and item["_id"] is not None:
                    item["_id"] = str(item["_id"])
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc


def docs_to_public(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [doc_to_public(d) for d in docs if d is not None]


def subdoc_to_public(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if doc is None:
        return None
    if "_id" in doc and doc["_id"] is not None:
        doc["_id"] = str(doc["_id"])
    return doc
