from datetime import datetime, timedelta
import json
from typing import Tuple

from fastapi import APIRouter, Response, Depends, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.db import get_db
from app.models import User
from app.services.user import UserService
from app.repositories.user import UserRepository
from app.errors import(
     UserAlreadyExists, UserNotFound, 
     InvalidCredentials, InvalidToken,
)
from app.config import Config
from app.auth.service import AuthService
from app.auth.dependencies import (
    get_current_user, RefreshTokenDepends,
    AccessTokenDepends,
)
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
    create_token,
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


@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_db)):
    email = login_data.email
    password = login_data.password

    user = await user_repository.get_user_by_email(email, session)
    if user is not None:
        # user_data = UserResponse(**user)
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            auth_service = AuthService()
            response = await auth_service.create_auth_response(user, session)
            return response
    raise InvalidCredentials()


@auth_router.post("/logout")
async def logout(
    response: Response,
    session: AsyncSession=Depends(get_db), 
    access_token_data: dict=Depends(AccessTokenDepends()),  
    refresh_token_data: dict=Depends(RefreshTokenDepends()),
):    
    await user_service.marking_tokens_as_expired(refresh_token_data, access_token_data, session)
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


@auth_router.post("/refresh")
async def refresh(
    session: AsyncSession=Depends(get_db), 
    refresh_token_data: dict=Depends(RefreshTokenDepends()),
):
    email = refresh_token_data["user"]["email"]
    user = await user_repository.get_user_by_email(email, session)
    access_token, _ = create_token(
        user_data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        },
        refresh=False
    )
    response = JSONResponse(
        content={"message": "refreshed"}
    )
    response.headers["Authorization"] = f"Bearer {access_token}"
    return response
    

@auth_router.post("/current_user", response_model=UserResponse)
async def current_user(
    user: User=Depends(get_current_user)
):
    return user