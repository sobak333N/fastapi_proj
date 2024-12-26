from typing import Union
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.db import get_db
from app.config import Config
from app.models.user import User, Roles2
from app.schemas import UserResponse, InstructorResponse, StudentResponse
from app.repositories import UserRepository
from app.services import UserService
from app.auth.utils import create_token, encode_finger_print
from app.auth.schemas import (
    StudentCreateModel,
    InstructorCreateModel,
    AdminCreateModel,
)


class AuthService:
    async def mail_for_admin(self, admin_data: AdminCreateModel, session: AsyncSession):
        """
        Logic to send mail to admin mail with invation link for creating account
        """

    async def signup(self, user_data: Union[StudentCreateModel,InstructorCreateModel], session: AsyncSession):
        user_service = UserService()
        await user_service.set_temporary_token(user_data, session)
        return {"message": "Go to link in email to verify account"}


    def generate_differents_profile(self, user: User):
        if user.role == Roles2.student or user.role == Roles2.student.value:
            for attr, value in user.student.__dict__.items():
                if not attr.startswith('_'):
                    setattr(user, attr, value)
            return StudentResponse(**user.__dict__)
        elif user.role == Roles2.instructor or user.role == Roles2.instructor.value: 
            for attr, value in user.instructor.__dict__.items():
                if not attr.startswith('_'):
                    setattr(user, attr, value)
            return InstructorResponse(**user.__dict__)
        elif user.role == Roles2.admin or user.role == Roles2.admin.value: 
            return UserResponse(**user.__dict__)


    async def create_auth_response(self, user: User, finger_print_data: dict, session: AsyncSession):
        access_token, _ = create_token(
            user_data={
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role
            },
            refresh=False
        )


        finger_print = encode_finger_print(finger_print_data)
        user_repository = UserRepository()

        refresh_token = await user_repository.finger_print_exists(finger_print, session)
        if not refresh_token:
            refresh_token, refresh_exp = create_token(
                user_data={
                    "user_id": user.user_id,
                    "email": user.email,
                },
                refresh=True
            )
            await user_repository.add_refresh_token(
                user_id=user.user_id,
                refresh_token=refresh_token,
                finger_print=finger_print,
                expiresIn=int(refresh_exp.timestamp()),
                session=session
            )
        else:
            refresh_token = refresh_token.refresh_token

        response_user_data = self.generate_differents_profile(user)
        response = JSONResponse(
            content={
                "message": "Login successful",
                "user": jsonable_encoder(response_user_data)
            }
        )
        response.headers["Authorization"] = f"Bearer {access_token}"
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=timedelta(days=Config.JWT_REFRESH_EXP_DAYS),
            secure=True,
            samesite="Strict",
        )
        return response