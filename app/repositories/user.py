from fastapi import Depends, Request, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.core.db import get_db
from app.models import User, RefreshToken

from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_passwd_hash


class UserRepository:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
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