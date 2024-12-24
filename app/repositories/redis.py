from functools import wraps
import json
from typing import Optional, Callable

import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.config import Config


class RedisClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, db_num: int=0):
        self.redis_client: Optional[Redis] = None
        self.db_num: int = db_num

    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = aioredis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_INNER_PORT,
                db=self.db_num,
                encoding="utf-8"
            )
        return self.redis_client


class RedisCategory(RedisClass):
    _instance = None

    def __init__(self, db_num: int=1):
        self.redis_client: Optional[Redis] = None
        self.db_num: int = db_num


    @classmethod
    def cache(cls, key_prefix: str):
        def inner_decorator(function: Callable):
            @wraps(function)
            async def wrapper(*args, **kwargs):
                key_suffix: str = None
                for arg in args:
                    if isinstance(arg, int):
                        key_suffix = str(arg)
                        break
                key = key_prefix+key_suffix
                instance = cls()
                redis_client = await instance.get_redis_client()
                result = await redis_client.get(key)
                if result:
                    # print("XXXX")
                    return json.loads(result)
                result = await function(*args, **kwargs)
                await redis_client.set(name=key, value=json.dumps(result), ex=60*60*24*14)
                return result
            return wrapper
        return inner_decorator 


    @classmethod
    def cache(cls, key_prefix: str):
        def inner_decorator(function: Callable):
            @wraps(function)
            async def wrapper(*args, **kwargs):
                key_suffix: str = None
                for arg in args:
                    if isinstance(arg, int):
                        key_suffix = str(arg)
                        break
                key = key_prefix+key_suffix
                instance = cls()
                redis_client = await instance.get_redis_client()
                result = await redis_client.get(key)
                if result:
                    # print("XXXX")
                    return json.loads(result)
                result = await function(*args, **kwargs)
                await redis_client.set(name=key, value=json.dumps(result), ex=60*60*24*14)
                return result
            return wrapper
        return inner_decorator 