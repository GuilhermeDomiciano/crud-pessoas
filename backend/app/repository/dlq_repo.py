from __future__ import annotations

import json
from typing import Any

from aio_pika import ExchangeType, connect_robust
from aio_pika.exceptions import QueueEmpty

from messaging.rabbitmq import DLQ_NAME, DLQ_ROUTING_KEY, DLX_NAME
from settings import settings


class DlqRepository:
    async def peek(self, limit: int) -> list[dict[str, Any]]:
        if not settings.rabbitmq_url:
            return []

        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()

        dlx = await channel.declare_exchange(DLX_NAME, ExchangeType.DIRECT, durable=True)
        dlq = await channel.declare_queue(DLQ_NAME, durable=True)
        await dlq.bind(dlx, routing_key=DLQ_ROUTING_KEY)

        items: list[dict[str, Any]] = []
        for _ in range(limit):
            try:
                message = await dlq.get(no_ack=False)
            except QueueEmpty:
                break
            try:
                payload = json.loads(message.body.decode("utf-8"))
            except Exception:
                payload = {"_raw": message.body.decode("utf-8", errors="ignore")}
            items.append(payload)
            await message.nack(requeue=True)

        await connection.close()
        return items


def get_dlq_repository() -> DlqRepository:
    return DlqRepository()


