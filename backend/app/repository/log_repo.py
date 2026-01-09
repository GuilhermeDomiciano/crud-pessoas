from __future__ import annotations

from db.database import get_logs_db


class LogRepository:
    def __init__(self):
        self._collection = get_logs_db()["request_logs"]

    async def find_logs(self, query: dict, limit: int):
        cursor = (
            self._collection.find(query)
            .sort([("requestTime", -1), ("_id", -1)])
            .limit(limit)
        )
        return [doc async for doc in cursor]


def get_log_repository() -> LogRepository:
    return LogRepository()


