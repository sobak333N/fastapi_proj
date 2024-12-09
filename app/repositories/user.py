from typing import Type, TypeVar, List

from fastapi import Depends, Request, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.core.db import get_db
from app.models import User, RefreshToken
from app.models.user import Roles2
from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_passwd_hash


T = TypeVar('T')

class UserRepository:
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


    async def create_user(self, user_data_dict: dict, session: AsyncSession):
        new_user = User(**user_data_dict)
        session.add(new_user)
        await session.commit()
        return new_user


    async def update_user(self, user: User , user_data: dict, session: AsyncSession):
        for attr, value in user_data.items():
            setattr(user, attr, value)

        return user

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
        return result is not None
    

class BaseRepository:
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> T:
        statement = select(self.model).where(self.model.user_id == user_id)
        result = await session.execute(statement)
        instance = result.scalars().first()
        return instance

    async def add(self, data: dict, session: AsyncSession) -> T:
        instance = self.model(**data)
        session.add(instance)
        await session.commit()
        return instance
