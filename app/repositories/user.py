from fastapi import Depends, Request, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db, get_transaction_db
from app.models import User

from app.auth.schemas import UserCreateModel
from app.auth.utils import generate_passwd_hash


class UserRepository:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.first()
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
