from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.config import Config

class RedisAuth:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.redis_client: Optional[Redis] = None

    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = aioredis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_INNER_PORT,
                db=0,
                encoding="utf-8"
            )
        return self.redis_client
# token_blocklist = aioredis.from_url(Config.REDIS_URL)

# async def add_jti_to_blocklist(jti: str) -> None:
#     await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


# async def token_in_blocklist(jti: str) -> bool:
#     jti = await token_blocklist.get(jti)

#     return jti is not None