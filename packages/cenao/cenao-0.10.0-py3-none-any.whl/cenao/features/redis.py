import async_timeout
from asyncio import Lock, Queue
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncContextManager, Any, Dict, List, Optional

import aioredis
import aioredis_cluster

from cenao.app import AppFeature


class TeeChannel:
    _tee: 'Tee'
    _queue: Queue

    def __init__(self, tee: 'Tee'):
        self._tee = tee
        self._queue = Queue()

    async def get(self) -> Any:
        if self._queue.empty() and not self._tee.lock.locked():
            async with self._tee.lock:
                await self._tee.get()

        return await self._queue.get()

    async def get_timeout(self, timeout: float):
        async with async_timeout.timeout(timeout):
            return await self.get()

    def put(self, item):
        self._queue.put_nowait(item)

    async def __anext__(self) -> Any:
        return await self.get()


class Tee:
    redis: aioredis.Redis
    channel: str
    lock: Lock = Lock()
    _channel: Optional[aioredis.Channel]
    _channels: List[TeeChannel] = []

    def __init__(self, redis: aioredis.Redis, channel: str):
        self.redis = redis
        self.channel = channel

    async def get(self):
        if not self._channel:
            raise RuntimeError('Must initialize channel first')

        item = await self._channel.get()
        for ch in self._channels:
            ch.put(item)

    async def _start(self):
        channels = await self.redis.subscribe(self.channel)
        self._channel = channels[0]

    async def _stop(self):
        try:
            await self.redis.unsubscribe(self.channel)
        except Exception:
            pass
        finally:
            self._channel = None

    @asynccontextmanager
    async def get_channel(self) -> AsyncGenerator[TeeChannel, None]:
        if self.empty():
            await self._start()

        tee_channel = TeeChannel(self)
        self._channels.append(tee_channel)

        try:
            yield tee_channel
        finally:
            self._channels.remove(tee_channel)
            if self.empty():
                await self._stop()

    def empty(self) -> bool:
        return len(self._channels) == 0


class TeeKeeper:
    redis: aioredis.Redis
    _tees: Dict[str, Tee] = {}

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    @asynccontextmanager
    async def get_tee_channel(self, channel: str) -> AsyncGenerator[TeeChannel, None]:
        if channel not in self._tees:
            self._tees[channel] = Tee(self.redis, channel)
        tee = self._tees[channel]

        try:
            async with tee.get_channel() as tee_channel:
                yield tee_channel
        finally:
            if tee.empty():
                del self._tees[channel]


class RedisAppFeature(AppFeature):
    """
    Cenao feature for Redis support.
    By default tries connect to `redis://172.17.0.1`, which can be changed via `nodes` config parameter.
    """
    NAME = 'redis'

    _client: aioredis.Redis
    _tee_keeper: Optional[TeeKeeper] = None

    async def on_startup(self):
        cluster = self.config.get('cluster', False)
        follow_cluster = self.config.get('follow_cluster', True)
        nodes = self.config.get('nodes', 'redis://172.17.0.1').split(',')

        kwargs = {
            "follow_cluster": follow_cluster,
        }

        pool_minsize = self.config.get("pool_minsize")
        if pool_minsize:
            kwargs["minsize"] = pool_minsize

        pool_maxsize = self.config.get("pool_maxsize")
        if pool_maxsize:
            kwargs["maxsize"] = pool_maxsize

        username = self.config.get("username")
        if username:
            kwargs["username"] = username

        password = self.config.get("password")
        if password:
            kwargs["password"] = password

        if cluster:
            self._client = await aioredis_cluster.create_redis_pool(nodes, **kwargs)
        else:
            self._client = await aioredis.create_redis_pool(nodes[0], **kwargs)

        await self._client.ping()

    async def on_shutdown(self):
        if self._client:
            self._client.close()
            await self._client.wait_closed()

    async def check_health(self) -> bool:
        if self._client:
            await self._client.ping()
        return True

    @property
    def client(self) -> aioredis.Redis:
        """
        Redis instance getter
        :return: A Redis client instance
        """
        if not self._client:
            raise RuntimeError("Redis client is not initialized yet")

        return self._client

    def subscribe(self, channel: str) -> AsyncContextManager[TeeChannel]:
        """
        Subscribe (and reuse existing connection) to Redis pubsub channel
        :return: A Tee channel handler
        """
        if not self._client:
            raise RuntimeError('Redis connection must be established first')

        if not self._tee_keeper:
            self._tee_keeper = TeeKeeper(self.client)

        return self._tee_keeper.get_tee_channel(channel)
