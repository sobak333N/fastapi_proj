import json
from datetime import datetime

from fastapi import Depends, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.core.db import get_db
from app.models import User, RefreshToken
from app.models.user import Roles2
from app.repositories import (
    UserRepository, 
    InstructorRepository, 
    StudentRepository,
)
from app.services.base_service import BaseService
from app.auth.schemas import UserCreateModel
from app.auth.utils import (
    generate_passwd_hash, 
    generate_random_token,
    verify_password,
)
from app.auth.redis_auth import RedisAuth
from app.errors import (
    UserAlreadyExists,
    EmailTokenError,
    InstanceDoesntExists,
    InvalidCredentials,
)



class UserService(BaseService):

    def __init__(self):
        super().__init__(UserRepository, "User")
        self.redis_auth = RedisAuth()
        self.instructor_repository = InstructorRepository()
        self.student_repository = StudentRepository()

    async def get_user_by_email(self, email: str, session: AsyncSession):
        user = await self.repository.get_user_by_email(email, session)
        # if user is None:
            # InstanceDoesntExists(model_name=self.model_name, detail=self.model_name)
        return user
        
    async def change_password(
        self,
        old_password: str,
        password: str,
        user: User,
        session: AsyncSession,
    ):
        password_valid = verify_password(old_password, user.password_hash)
        if not password_valid:
            raise InvalidCredentials()
        password_hash = generate_passwd_hash(password)
        await self.repository.set_value(user, "password_hash", password_hash, session)


    async def set_temporary_token(
        self,
        user_data: UserCreateModel,
        session: AsyncSession
    ) -> None:
        redis_client = await self.redis_auth.get_redis_client()
        user_exists = await self.repository.user_exists(user_data.email, session)

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
        redis_client = await self.redis_auth.get_redis_client()
        user_data_json = await redis_client.get(token)
        await redis_client.delete(token)
        if not user_data_json:
            raise EmailTokenError()

        full_user_data = json.loads(user_data_json)
        user_data = {
            "first_name": full_user_data.get("first_name"),
            "last_name": full_user_data.get("last_name"),
            "second_name": full_user_data.get("second_name"),
            "birthdate": (
                datetime.strptime(full_user_data.get("birthdate"), '%Y-%m-%dT%H:%M:%S')
                if "birthdate" in full_user_data and isinstance(full_user_data.get("birthdate"), str)
                else None
            ),
            "email": full_user_data.get("email"),
            "password_hash": full_user_data.get("password_hash"),
            "role": Roles2[full_user_data.get("role")],
        }
        new_user = await self.repository.create_instance(session, **user_data, no_commit=True)
        if user_data["role"] == Roles2.student:
            student_data = {
                "user_id": new_user.user_id,
                "subscription_plan": full_user_data.get("subscription_plan"),
                "learning_style": full_user_data.get("learning_style"),
            }
            student = await self.student_repository.create_instance(session, **student_data, no_commit=True)
            new_user.student = student
        elif user_data["role"] == Roles2.instructor:
            instructor_data = {
                "user_id": new_user.user_id,
                "education": full_user_data.get("education"),
                "academic_degree": full_user_data.get("academic_degree"),
                "academical_experience": full_user_data.get("academical_experience"),
                "H_index": full_user_data.get("H_index"),
            }
            instructor = await self.instructor_repository.create_instance(session, **instructor_data, no_commit=True)
            new_user.instructor = instructor
        await session.commit()
        return new_user
    
    async def marking_tokens_as_expired(
        self, 
        refresh_token_data: dict,
        access_token_data: str,
        session: AsyncSession,        
    ) -> None:
        await self.repository.remove_refresh_token(refresh_token_data["token"], session)
        refresh_token_data.pop("token")
        redis_client = await self.redis_auth.get_redis_client()
        await redis_client.set(name=access_token_data["jti"], value="exp", ex=Config.JWT_ACCESS_EXP_MINUTES*60)

    async def token_in_blocklist(self, jti: str) -> bool:
        redis_client = await self.redis_auth.get_redis_client()
        jti = await redis_client.get(jti)
        return jti is not None