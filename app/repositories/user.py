from typing import Type, TypeVar, List, Coroutine, Optional
from functools import wraps
from datetime import datetime
from enum import Enum
import json

from fastapi import Depends, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, update


from app.models import User, RefreshToken, Instructor, Student
from app.models.user import Roles2
from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_passwd_hash
from app.repositories.base_repository import BaseRepository
from app.repositories.redis import RedisInstanced
from app.task_manager import TaskManager

T = TypeVar('T')


class RedisUser(RedisInstanced):
    @classmethod
    def get_cache(cls, key_prefix: str):
        def inner_decorator(function: Coroutine):
            @wraps(function)
            async def wrapper(*args, **kwargs):
                key_suffix: str = None
                for arg in args:
                    if isinstance(arg, str):
                        key_suffix = str(arg)
                key = key_prefix+key_suffix
                instance = cls()
                redis_client = await instance.get_redis_client()
                result = await redis_client.get(key)
                if result:
                    user = json.loads(result)
                    instructor_data = user.pop("instructor", None)
                    if instructor_data:
                        user["instructor"] = Instructor(**instructor_data)
                    student_data = user.pop("student", None)
                    if student_data:
                        user["student"] = Student(**student_data)

                    user['birthdate'] = datetime.strptime(user['birthdate'], "%Y-%m-%dT%H:%M:%S")
                    user['created_at'] = datetime.strptime(user['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
                    user = User(**user)
                    return user

                result = await function(*args, **kwargs)
                if result:
                    await redis_client.set(
                        name=key, 
                        value=json.dumps((jsonable_encoder(result))),
                        ex=60*60*24
                    )
                return result
            return wrapper
        return inner_decorator 


    @classmethod
    def del_cache(cls, key_prefix: str="example"):
        def inner_decorator(function: Coroutine):
            @wraps(function)
            async def wrapper(*args, **kwargs):                
                key_suffix: str = None
                for arg in args:
                    if isinstance(arg, User):
                        key_suffix = str(arg.email)
                        break        
                key = key_prefix+key_suffix
                instance = cls()
                redis_client = await instance.get_redis_client()
                result = await function(*args, **kwargs)
                await TaskManager.create_task(redis_client.delete(key))
                return result
            return wrapper
        return inner_decorator 



class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    @RedisUser.get_cache(key_prefix="current_user")
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalars().first()
        if user:
            if user.role == Roles2.student:
                statement = statement.options(selectinload(User.student))
            elif user.role == Roles2.instructor:
                statement = statement.options(selectinload(User.instructor))
            statement = statement.options(noload(User.refresh_token))

            result = await session.execute(statement)
            user = result.scalars().first()
        return user


    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def add_refresh_token(
        self,
        user_id: int,
        refresh_token: str,
        finger_print: str,
        expiresIn: int,       
        session: AsyncSession,
    ) -> None:
        refresh_token = RefreshToken(
            user_id=user_id,
            refresh_token=refresh_token,
            finger_print=finger_print,
            expiresIn=expiresIn,
        )     
        session.add(refresh_token)
        await session.commit()

    async def remove_refresh_token(self, refresh_token: str, session: AsyncSession) -> None:
        statement = delete(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
        await session.execute(statement)
        await session.commit()

    async def refresh_token_exists(self, refresh_token: str, session: AsyncSession) -> bool:
        statement = select(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
        result = await session.execute(statement)
        result = result.scalars().first()
        return result is not None

    async def finger_print_exists(self, finger_print: str, session: AsyncSession) -> RefreshToken:
        statement = select(RefreshToken).where(RefreshToken.finger_print == finger_print)
        result = await session.execute(statement)
        result = result.scalars().first()
        return result




class BaseUserRepository(BaseRepository):
    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> T:
        statement = select(self.model).where(self.model.user_id == user_id)
        result = await session.execute(statement)
        instance = result.scalars().first()
        return instance
    
    # async def update_instance(self, instance: T, session: AsyncSession, **kwargs) -> Optional[T]:
    #     # if kwargs:
    #         # for attr, value in kwargs.items():
    #             # setattr(instance, attr, value)
    #     for attr, value in instance.__dict__.items():
    #         setattr(instance, attr, value)
    #     session.add(instance)
    #     print("BEFORE COMMIT2")
    #     print(session.__dict__)
    #     await session.commit()
    #     print("AFTER COMMIT2")
    #     return instance