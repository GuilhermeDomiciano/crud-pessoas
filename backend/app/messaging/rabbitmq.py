from __future__ import annotations

import json
import logging
from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
)
from aiormq.exceptions import ChannelPreconditionFailed

from settings import settings

LOG_EXCHANGE_NAME = "logs.exchange"
LOG_QUEUE_NAME = "logs.queue"
LOG_ROUTING_KEY = "logs.write"
LOG_RETRY_EXCHANGE_NAME = "logs.retry.exchange"
LOG_RETRY_QUEUE_NAME = "logs.retry.queue"
LOG_RETRY_ROUTING_KEY = "logs.retry"
LOG_RETRY_DELAY_MS = 1000
DLX_NAME = "logs.dlx"
DLQ_NAME = "logs.dlq"
DLQ_ROUTING_KEY = "logs.dlq"

_connection: AbstractRobustConnection | None = None
_channel: AbstractRobustChannel | None = None
_exchange: AbstractRobustExchange | None = None
logger = logging.getLogger(__name__)


async def _declare_queue_with_recreate(
    connection: AbstractRobustConnection,
    channel: AbstractRobustChannel,
    name: str,
    **kwargs: Any,
):
    try:
        return channel, await channel.declare_queue(name, **kwargs)
    except ChannelPreconditionFailed:
        logger.warning("Recreating queue with new arguments: %s", name)
        try:
            tmp = await connection.channel()
            await tmp.queue_delete(name, if_unused=False, if_empty=False)
            await tmp.close()
        except Exception:
            pass
        try:
            if channel.is_closed:
                channel = await connection.channel(publisher_confirms=True)
        except Exception:
            channel = await connection.channel(publisher_confirms=True)
        return channel, await channel.declare_queue(name, **kwargs)


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
    retry_exchange = await _channel.declare_exchange(
        LOG_RETRY_EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    _channel, queue = await _declare_queue_with_recreate(
        _connection,
        _channel,
        LOG_QUEUE_NAME,
        durable=True,
        arguments={
            "x-dead-letter-exchange": LOG_RETRY_EXCHANGE_NAME,
            "x-dead-letter-routing-key": LOG_RETRY_ROUTING_KEY,
        },
    )
    await queue.bind(exchange, routing_key=LOG_ROUTING_KEY)
    _channel, retry_queue = await _declare_queue_with_recreate(
        _connection,
        _channel,
        LOG_RETRY_QUEUE_NAME,
        durable=True,
        arguments={
            "x-message-ttl": LOG_RETRY_DELAY_MS,
            "x-dead-letter-exchange": LOG_EXCHANGE_NAME,
            "x-dead-letter-routing-key": LOG_ROUTING_KEY,
        },
    )
    await retry_queue.bind(retry_exchange, routing_key=LOG_RETRY_ROUTING_KEY)
    dlx = await _channel.declare_exchange(
        DLX_NAME,
        ExchangeType.DIRECT,
        durable=True,
    )
    _channel, dlq = await _declare_queue_with_recreate(
        _connection,
        _channel,
        DLQ_NAME,
        durable=True,
    )
    await dlq.bind(dlx, routing_key=DLQ_ROUTING_KEY)
    _exchange = exchange


async def close_rabbitmq() -> None:
    global _connection, _channel, _exchange
    if _connection is not None:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None


async def ping_rabbitmq() -> bool:
    if not settings.rabbitmq_url:
        return False
    if _connection is not None and not _connection.is_closed:
        return True
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        await connection.close()
        return True
    except Exception:
        return False


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


