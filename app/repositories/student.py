# from typing import Type, TypeVar, List

# from fastapi import Depends, Request, status
# from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import delete

# from app.core.db import get_db
# from app.models import User, RefreshToken
# from app.auth.schemas import UserCreateModel
# from app.auth.utils import generate_passwd_hash
from app.repositories.user import BaseUserRepository
from app.models import Student


class StudentRepository(BaseUserRepository):
    def __init__(self):
        return super().__init__(Student)


