from __future__ import annotations

import hashlib
import json
from typing import Any


_PREFIX = "app:"
LIST_VERSION_KEY = f"{_PREFIX}persons:list:ver"


def person_key(person_id: str) -> str:
    return f"{_PREFIX}person:{person_id}"


def normalize_query(params: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip() == "":
                continue
            normalized[key] = value.strip()
            continue
        if isinstance(value, (list, tuple)):
            if not value:
                continue
            normalized[key] = list(value)
            continue
        normalized[key] = value
    return normalized


def hash_query(params: dict[str, Any]) -> str:
    normalized = normalize_query(params)
    payload = json.dumps(
        normalized,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def persons_list_key(version: int, params: dict[str, Any]) -> str:
    return f"{_PREFIX}persons:list:v{version}:{hash_query(params)}"
