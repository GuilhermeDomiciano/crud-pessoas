from __future__ import annotations

from typing import Any, Dict, List, Optional
from bson import ObjectId

def to_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise ValueError("id inválido")
    return ObjectId(id_str)

def doc_to_public(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if doc is None:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

def docs_to_public(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [doc_to_public(d) for d in docs if d is not None]