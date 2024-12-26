from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.config import Config
from app.repositories.redis import RedisClass


class RedisAuth(RedisClass):
    pass