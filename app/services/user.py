import json

from fastapi import Depends, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.core.db import get_db
from app.models import User
from app.repositories import UserRepository
from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_passwd_hash, generate_random_token
from app.auth.redis_auth import RedisAuth
from app.errors import (
    UserAlreadyExists,
    EmailTokenError,
)



class UserService:

    def __init__(self):
        self.redis_auth = RedisAuth()

    async def set_temporary_token(
        self,
        user_data: UserCreateModel,
        session: AsyncSession
    ) -> None:
        user_repository = UserRepository()
        redis_client = await self.redis_auth.get_redis_client()
        user_exists = await user_repository.user_exists(user_data.email, session)

        if user_exists:
            raise UserAlreadyExists()

        token = generate_random_token()

        user_data_dict = jsonable_encoder(user_data)
        user_data_dict["password_hash"] = generate_passwd_hash(user_data_dict["password"])
        user_data_dict.pop("password")
        user_data_json = json.dumps(user_data_dict)

        await redis_client.set(token, user_data_json, ex=Config.EMAIL_TOKENS_EX_MINUTES*60)


    async def accept_register(
        self,
        token: str,
        session: AsyncSession,
    ) -> User:
        user_repository = UserRepository()
        redis_client = await self.redis_auth.get_redis_client()
        user_data_json = await redis_client.get(token)

        if not user_data_json:
            raise EmailTokenError()

        user_data = json.loads(user_data_json)
        print()
        new_user = await user_repository.create_user(user_data, session)

        return new_user