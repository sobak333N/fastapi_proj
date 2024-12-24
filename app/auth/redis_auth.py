from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.config import Config
from app.repositories.redis import RedisClass


class RedisAuth(RedisClass):
    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = aioredis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_INNER_PORT,
                db=0,
                encoding="utf-8"
            )
        return self.redis_client
