from aioredis import Redis

from cenao.app import AppFeature


class RedisStorageAppFeature(AppFeature):
    NAME = 'redis_storage'

    redis: Redis

    def __init__(self, redis: str = 'redis', name=None):
        super().__init__(name)
        self._redis = redis

    def on_init(self):
        self.redis = self.app.ft.get(self._redis)
