from __future__ import annotations

from datetime import datetime

from bson import ObjectId

from repository.log_repo import LogRepository


class LogService:
    def __init__(self, repo: LogRepository):
        self._repo = repo

    @staticmethod
    def _build_cursor_filter(cursor: str | None) -> dict:
        if not cursor:
            return {}
        try:
            raw_time, raw_id = cursor.split("|", 1)
            cursor_time = datetime.fromisoformat(raw_time)
            cursor_id = ObjectId(raw_id)
        except Exception:
            return {}
        return {
            "$or": [
                {"requestTime": {"$lt": cursor_time}},
                {"requestTime": cursor_time, "_id": {"$lt": cursor_id}},
            ]
        }

    @staticmethod
    def _make_cursor(doc: dict) -> str | None:
        req_time = doc.get("requestTime")
        doc_id = doc.get("_id")
        if not isinstance(req_time, datetime) or not isinstance(doc_id, ObjectId):
            return None
        return f"{req_time.isoformat()}|{str(doc_id)}"

    @staticmethod
    def _doc_to_public(doc: dict) -> dict:
        if "_id" in doc and doc["_id"] is not None:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def _apply_event_type_filter(query: dict, event_type: str | None) -> None:
        if not event_type:
            return
        et = event_type.lower()
        if et == "error":
            query["statusCode"] = {"$gte": 400}
        elif et == "success":
            query["statusCode"] = {"$lt": 400}

    async def listar_logs(
        self,
        limit: int,
        cursor: str | None,
        status_code: int | None,
        method: str | None,
        url: str | None,
        event_type: str | None,
        person_id: str | None = None,
    ) -> dict:
        query: dict = {}
        if status_code is not None:
            query["statusCode"] = status_code
        if method:
            query["method"] = method.upper()
        if url:
            query["url"] = url
        if person_id:
            query["params.id"] = person_id
        self._apply_event_type_filter(query, event_type)
        query.update(self._build_cursor_filter(cursor))

        docs = await self._repo.find_logs(query, limit)
        items = [self._doc_to_public(doc) for doc in docs]
        next_cursor = self._make_cursor(docs[-1]) if docs else None
        return {"items": items, "nextCursor": next_cursor}
