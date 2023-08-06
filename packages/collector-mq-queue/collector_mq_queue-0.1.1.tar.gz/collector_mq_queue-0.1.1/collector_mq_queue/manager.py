from dataclasses import dataclass
import asyncio
import aio_pika
import aio_pika.abc as base_pika
from typing import Optional, Dict, List
import ujson as json
from aio_pika.pool import Pool
import pika


@dataclass
class AMQP_Manager:
    """
    Create a specific connection to queue
    """
    user: str
    password: str
    host: str
    port: int
    exchange_name: str
    queues: List[str]
    # loop: Optional[asyncio.AbstractEventLoop]
    # connection_pool: Optional[Pool]
    # channel_pool: Optional[Pool]
    n_pool: int = 10
    n_chann: int = 1
    ttl: int = 360
    active = False

    def __post_init__(self):
        self.loop = asyncio.get_event_loop()

    async def start(self):
        self.connection_pool = Pool(self.connect,
                                    max_size=self.n_pool)
        self.channel_pool = Pool(self.get_channel,
                                 max_size=self.n_chann)

    @property
    def url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"

    def add_queue(self, queue_name):
        if queue_name not in self.queues:
            self.queues.append(queue_name)

    async def connect(self):
        result = await aio_pika.connect_robust(self.url, loop=self.loop)
        self.active = True
        return result

    async def close(self):
        self.active = False

    async def get_channel(self):
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def publish(self, msg: dict, routing_key: str):
        if routing_key in self.queues:
            async with self.channel_pool.acquire() as channel:
                exchange = await channel.declare_exchange(
                    self.exchange_name, durable=True)
                queue = await channel.declare_queue(
                    routing_key, durable=True)
                await queue.bind(exchange, routing_key)
                msg_serialized = json.dumps(
                    msg, default=lambda x: str(x)).encode()
                pika_msg = aio_pika.Message(
                    body=msg_serialized,
                    expiration=self.ttl)
                await exchange.publish(pika_msg,
                                       routing_key)
        else:
            print(f"Queue routed as '{routing_key}' doesn't exists")
