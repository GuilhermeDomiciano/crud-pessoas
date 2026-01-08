from __future__ import annotations

from settings import settings


def _parse_keys(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def is_valid_api_key(key: str | None) -> bool:
    if not key:
        return False
    keys = _parse_keys(settings.api_keys)
    return key in keys
