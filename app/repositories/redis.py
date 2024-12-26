from functools import wraps
from typing import Optional, Callable, Coroutine
import asyncio
import json
import inspect

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import Config
from app.task_manager import TaskManager 


class RedisClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, db_num: int=0, key_prefix: str="example"):
        self.redis_client: Optional[Redis] = None
        self.db_num: int = db_num
        self.key_prefix: str = key_prefix

    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = aioredis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_INNER_PORT,
                db=self.db_num,
                encoding="utf-8"
            )
        return self.redis_client

    @classmethod
    def get_cache(cls, key_prefix: str):
        def inner_decorator(function: Coroutine):
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
                    return json.loads(result)
                result = await function(*args, **kwargs)
                await redis_client.set(name=key, value=json.dumps(result), ex=60*60*24*14)
                return result
            return wrapper
        return inner_decorator 

    @classmethod
    def del_cache(cls):
        pass


class RedisPaged(RedisClass):
    _instance = None

    def __init__(self, db_num: int=1, key_prefix: str="example"):
        self.redis_client: Optional[Redis] = None
        self.db_num: int = db_num
        self.key_prefix: str = key_prefix

    @classmethod
    def del_cache(cls, key_prefix: str="example"):
        def inner_decorator(function: Coroutine):
            @wraps(function)
            async def wrapper(*args, **kwargs):                
                keys_to_delete = []
                instance = cls()
                result = await function(*args, **kwargs)

                async def delete_keys(key_prefix: str, redis_client: Redis) -> None:
                    cursor = 0
                    key_prefix += "*"

                    while True:
                        cursor, keys = await redis_client.scan(cursor=cursor, match=key_prefix, count=100)
                        keys_to_delete.extend(keys)
                        if cursor == 0:
                            break

                    if keys_to_delete:
                        await redis_client.delete(*keys_to_delete)

                instance = cls()
                redis_client = await instance.get_redis_client()
                await TaskManager.create_task(delete_keys(key_prefix, redis_client))
                return result
            return wrapper
        return inner_decorator 