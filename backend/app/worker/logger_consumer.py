from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError

from db.database import get_logs_db
from messaging.rabbitmq import (
    DLQ_NAME,
    DLQ_ROUTING_KEY,
    DLX_NAME,
    LOG_EXCHANGE_NAME,
    LOG_QUEUE_NAME,
    LOG_RETRY_DELAY_MS,
    LOG_RETRY_EXCHANGE_NAME,
    LOG_RETRY_QUEUE_NAME,
    LOG_RETRY_ROUTING_KEY,
    LOG_ROUTING_KEY,
    _declare_queue_with_recreate,
    ping_rabbitmq,
)
from model.log_message import LogMessage
from settings import settings

RETRY_MAX = 5

logger = logging.getLogger(__name__)


async def _setup_queue(connection, channel):
    exchange = await channel.declare_exchange(
        LOG_EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    retry_exchange = await channel.declare_exchange(
        LOG_RETRY_EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    channel, queue = await _declare_queue_with_recreate(
        connection,
        channel,
        LOG_QUEUE_NAME,
        durable=True,
        arguments={
            "x-dead-letter-exchange": LOG_RETRY_EXCHANGE_NAME,
            "x-dead-letter-routing-key": LOG_RETRY_ROUTING_KEY,
        },
    )
    await queue.bind(exchange, routing_key=LOG_ROUTING_KEY)
    channel, retry_queue = await _declare_queue_with_recreate(
        connection,
        channel,
        LOG_RETRY_QUEUE_NAME,
        durable=True,
        arguments={
            "x-message-ttl": LOG_RETRY_DELAY_MS,
            "x-dead-letter-exchange": LOG_EXCHANGE_NAME,
            "x-dead-letter-routing-key": LOG_ROUTING_KEY,
        },
    )
    await retry_queue.bind(retry_exchange, routing_key=LOG_RETRY_ROUTING_KEY)

    dlx = await channel.declare_exchange(
        DLX_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    channel, dlq = await _declare_queue_with_recreate(
        connection,
        channel,
        DLQ_NAME,
        durable=True,
    )
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


def _get_death_count(message: AbstractIncomingMessage) -> int:
    headers = message.headers or {}
    deaths = headers.get("x-death")
    if not isinstance(deaths, list):
        return 0
    total = 0
    for entry in deaths:
        if isinstance(entry, dict):
            count = entry.get("count", 0)
            if isinstance(count, int):
                total += count
    return total


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
        attempts = _get_death_count(message)
        if attempts >= RETRY_MAX:
            await _publish_dlq(dlx, message.body, message.content_type)
            await message.ack()
            return
        await message.reject(requeue=False)
        return

    await message.ack()


async def main() -> None:
    if not settings.rabbitmq_url:
        logger.error("RABBITMQ_URL not configured")
        return
    if settings.logger.upper() != "ON":
        logger.info("LOGGER=OFF, consumer disabled")
        return

    connection = await connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue, dlx = await _setup_queue(connection, channel)
    logger.info("logger-consumer is listening")

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
    if "--healthcheck" in sys.argv:
        ok = asyncio.run(ping_rabbitmq())
        sys.exit(0 if ok else 1)
    asyncio.run(main())

