from __future__ import annotations

from repository.dlq_repo import DlqRepository


class DlqService:
    def __init__(self, repo: DlqRepository):
        self._repo = repo

    async def listar_dlq(self, limit: int) -> dict[str, object]:
        items = await self._repo.peek(limit)
        return {"items": items}
