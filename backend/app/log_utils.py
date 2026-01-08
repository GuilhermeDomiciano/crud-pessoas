from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

DEFAULT_SENSITIVE_FIELDS = {
    "documentnumber",
    "email",
    "number",
    "password",
    "phonenumbers",
    "senha",
}


def mask_sensitive(
    data: Any,
    fields: Iterable[str] | None = None,
    mask: str = "***",
) -> Any:
    if data is None:
        return None
    field_set = {f.lower() for f in (fields or DEFAULT_SENSITIVE_FIELDS)}

    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in field_set:
                masked[key] = mask
            else:
                masked[key] = mask_sensitive(value, field_set, mask)
        return masked

    if isinstance(data, list):
        return [mask_sensitive(item, field_set, mask) for item in data]

    return data


def truncate_body(body: Any, max_bytes: int) -> tuple[Any, bool, int]:
    if body is None:
        return None, False, 0
    if max_bytes <= 0:
        return None, True, 0
    try:
        raw = json.dumps(body, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        size = len(raw)
    except (TypeError, ValueError):
        fallback = {"_type": type(body).__name__}
        raw = json.dumps(fallback, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        size = len(raw)
        return fallback, True, size
    if size <= max_bytes:
        return body, False, size
    truncated = raw[:max_bytes].decode("utf-8", errors="ignore")
    return {"_truncated": True, "value": truncated}, True, size

