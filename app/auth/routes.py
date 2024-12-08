from datetime import datetime, timedelta
import json


from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.db import get_db
from app.services.user import UserService
from app.repositories.user import UserRepository
from app.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from app.config import Config

from app.auth.redis_auth import RedisAuth
from app.auth.schemas import (
    UserCreateModel,
    UserLoginModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from app.schemas.user import UserResponse
from app.auth.utils import (
    generate_random_token,
    verify_password,
    generate_passwd_hash,
)


auth_router = APIRouter()
user_service = UserService()
user_repository = UserRepository()

# role_checker = RoleChecker(["admin", "user"])





@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, session: AsyncSession=Depends(get_db)):
    # """
    # Create user account using email, username, first_name, last_name, role
    # params:
    #     user_data: UserCreateModel
    # """

    await user_service.set_temporary_token(user_data, session)

    return {
        "message": "Go to link in email to verify account",
    }


@auth_router.get("/verify/{token}", response_model=UserResponse)
async def verify_user_account(token: str, session: AsyncSession=Depends(get_db)):
    new_user = await user_service.accept_register(token, session)
    new_user_dict = jsonable_encoder(new_user)
    user_data = UserResponse(**new_user_dict)
    return user_data


# @auth_router.post("/login")
# async def login_users(
#     login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
# ):
#     email = login_data.email
#     password = login_data.password

#     user = await user_service.get_user_by_email(email, session)

#     if user is not None:
#         password_valid = verify_password(password, user.password_hash)

#         if password_valid:
#             access_token = create_access_token(
#                 user_data={
#                     "email": user.email,
#                     "user_uid": str(user.uid),
#                     "role": user.role,
#                 }
#             )

#             refresh_token = create_access_token(
#                 user_data={"email": user.email, "user_uid": str(user.uid)},
#                 refresh=True,
#                 expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
#             )

#             return JSONResponse(
#                 content={
#                     "message": "Login successful",
#                     "access_token": access_token,
#                     "refresh_token": refresh_token,
#                     "user": {"email": user.email, "uid": str(user.uid)},
#                 }
#             )

#     raise InvalidCredentials()