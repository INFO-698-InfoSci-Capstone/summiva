from typing import Any, Callable, Dict, Optional
import json
import asyncio
import aio_pika
from aio_pika import Message, ExchangeType
import logging
from config.settings.settings import settings

logger = logging.getLogger(__name__)

class MessageQueue:
    _instance = None
    _connection = None
    _channel = None
    _exchanges: Dict[str, Any] = {}
    _queues: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageQueue, cls).__new__(cls)
        return cls._instance

    async def connect(self):
        """Connect to RabbitMQ"""
        if not self._connection:
            self._connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=30
            )
            self._channel = await self._connection.channel()
            logger.info("Connected to RabbitMQ")

    async def close(self):
        """Close RabbitMQ connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            logger.info("Disconnected from RabbitMQ")

    async def declare_exchange(self, name: str, type: ExchangeType = ExchangeType.TOPIC):
        """Declare an exchange"""
        if name not in self._exchanges:
            exchange = await self._channel.declare_exchange(
                name=name,
                type=type,
                durable=True
            )
            self._exchanges[name] = exchange
            logger.info(f"Declared exchange: {name}")

    async def declare_queue(self, name: str, exchange: Optional[str] = None, routing_key: Optional[str] = None):
        """Declare a queue and optionally bind it to an exchange"""
        if name not in self._queues:
            queue = await self._channel.declare_queue(
                name=name,
                durable=True
            )
            self._queues[name] = queue

            if exchange and routing_key:
                await queue.bind(self._exchanges[exchange], routing_key=routing_key)
                logger.info(f"Bound queue {name} to exchange {exchange} with routing key {routing_key}")

    async def publish(self, exchange: str, routing_key: str, message: Dict[str, Any]):
        """Publish a message to an exchange"""
        if exchange not in self._exchanges:
            await self.declare_exchange(exchange)

        message_body = json.dumps(message).encode()
        await self._exchanges[exchange].publish(
            Message(
                body=message_body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=routing_key
        )
        logger.debug(f"Published message to {exchange} with routing key {routing_key}")

    async def consume(self, queue: str, callback: Callable[[Dict[str, Any]], None]):
        """Consume messages from a queue"""
        if queue not in self._queues:
            await self.declare_queue(queue)

        async with self._queues[queue].iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        message_body = json.loads(message.body.decode())
                        await callback(message_body)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        # Implement dead letter queue or retry logic here 