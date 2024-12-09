from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.db import get_db
from app.config import Config
from app.models import User
from app.schemas import UserResponse
from app.repositories import UserRepository
from app.auth.utils import create_token


class AuthService:
    async def create_auth_response(self, user: User, session: AsyncSession):
        user_dict = jsonable_encoder(user)
        access_token, _ = create_token(
            user_data={
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role
            },
            refresh=False
        )
        refresh_token, refresh_exp = create_token(
            user_data={
                "user_id": user.user_id,
                "email": user.email,
            },
            refresh=True
        )

        user_repository = UserRepository()
        await user_repository.add_refresh_token(
            user_id=user.user_id,
            refresh_token=refresh_token,
            finger_print="finger",
            expiresIn=int(refresh_exp.timestamp()),
            session=session
        )
        response = JSONResponse(
            content={
                "message": "Login successful",
                "user": jsonable_encoder(UserResponse(**user_dict))
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