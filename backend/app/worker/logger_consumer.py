from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from db.database import get_logs_db
from messaging.rabbitmq import LOG_EXCHANGE_NAME, LOG_QUEUE_NAME, LOG_ROUTING_KEY
from model.log_message import LogMessage
from settings import settings

DLX_NAME = "logs.dlx"
DLQ_NAME = "logs.dlq"
DLQ_ROUTING_KEY = "logs.dlq"

logger = logging.getLogger(__name__)


async def _setup_queue(channel):
    exchange = await channel.declare_exchange(
        LOG_EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    queue = await channel.declare_queue(LOG_QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=LOG_ROUTING_KEY)

    dlx = await channel.declare_exchange(
        DLX_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    dlq = await channel.declare_queue(DLQ_NAME, durable=True)
    await dlq.bind(dlx, routing_key=DLQ_ROUTING_KEY)
    return queue, dlx


async def _publish_dlq(dlx, body: bytes, content_type: str | None) -> None:
    message = Message(
        body=body,
        content_type=content_type or "application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await dlx.publish(message, routing_key=DLQ_ROUTING_KEY, mandatory=False)


def _parse_payload(message: AbstractIncomingMessage) -> dict[str, Any] | None:
    try:
        payload = json.loads(message.body.decode("utf-8"))
    except Exception:
        return None
    try:
        LogMessage.model_validate(payload)
    except ValidationError:
        return None
    return payload


async def _handle_message(message: AbstractIncomingMessage, dlx) -> None:
    payload = _parse_payload(message)
    if payload is None:
        await _publish_dlq(dlx, message.body, message.content_type)
        await message.ack()
        return

    try:
        logs_db = get_logs_db()
        await logs_db["request_logs"].insert_one(payload)
    except Exception:
        await message.nack(requeue=True)
        return

    await message.ack()


async def main() -> None:
    if not settings.rabbitmq_url:
        logger.error("RABBITMQ_URL not configured")
        return

    connection = await connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue, dlx = await _setup_queue(channel)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                await _handle_message(message, dlx)
            except Exception:
                logger.exception("Unhandled error in log consumer")
                try:
                    await message.nack(requeue=True)
                except Exception:
                    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
