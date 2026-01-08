from __future__ import annotations

import json
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
)

from settings import settings

LOG_EXCHANGE_NAME = "logs.exchange"
LOG_QUEUE_NAME = "logs.queue"
LOG_ROUTING_KEY = "logs.write"

_connection: AbstractRobustConnection | None = None
_channel: AbstractRobustChannel | None = None
_exchange: AbstractRobustExchange | None = None


async def init_rabbitmq() -> None:
    if not settings.rabbitmq_url:
        return
    global _connection, _channel, _exchange
    if _connection is not None:
        return
    _connection = await connect_robust(settings.rabbitmq_url)
    _channel = await _connection.channel(publisher_confirms=True)
    exchange = await _channel.declare_exchange(
        LOG_EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    queue = await _channel.declare_queue(LOG_QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=LOG_ROUTING_KEY)
    _exchange = exchange


async def close_rabbitmq() -> None:
    global _connection, _channel, _exchange
    if _connection is not None:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None


async def publish_log_message(payload: dict[str, Any]) -> None:
    await init_rabbitmq()
    if _exchange is None:
        return
    body = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    message = Message(
        body=body,
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await _exchange.publish(message, routing_key=LOG_ROUTING_KEY, mandatory=True)
