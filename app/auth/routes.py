from datetime import datetime, timedelta
import json
from typing import Tuple, Type, Union

from fastapi import APIRouter, Response, Depends, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.db import get_db
from app.models.user import User, Roles2
from app.services.user import UserService
from app.repositories.user import UserRepository
from app.errors import(
    #  UserAlreadyExists, UserNotFound, 
     InvalidCredentials, InvalidToken,
)
from app.base_responses import BaseSuccessResponse
from app.config import Config
from app.auth.service import AuthService
from app.auth.dependencies import (
    get_current_user, RefreshTokenDepends,
    AccessTokenDepends, RoleChecker,
    FingerPrint,
)
from app.auth.schemas import (
    UserCreateModel,
    StudentCreateModel,
    InstructorCreateModel,
    AdminCreateModel,
    UserLoginModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from app.schemas import UserResponse, InstructorResponse, StudentResponse
from app.auth.utils import (
    generate_random_token,
    verify_password,
    generate_passwd_hash,
    create_token,
)


auth_router = APIRouter()
user_service = UserService()
auth_service = AuthService()

# role_checker = RoleChecker(["admin", "user"])



@auth_router.post("/signup/student", status_code=status.HTTP_201_CREATED)
async def create_student(
    user_data: StudentCreateModel,
    session: AsyncSession=Depends(get_db)
):
    print(user_data)
    return await auth_service.signup(user_data, session)


@auth_router.post("/signup/instructor", status_code=status.HTTP_201_CREATED)
async def create_instructor(
    user_data: InstructorCreateModel,
    session: AsyncSession=Depends(get_db)
):
    return await auth_service.signup(user_data, session)


@auth_router.get("/verify/{token}", response_model=UserResponse)
async def verify_user_account(
    token: str, 
    session: AsyncSession=Depends(get_db),
    finger_print_data: dict=Depends(FingerPrint()),
):
    new_user = await user_service.accept_register(token, session)
    response = await auth_service.create_auth_response(new_user, finger_print_data, session)
    return response


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, 
    finger_print_data: dict=Depends(FingerPrint()),
    session: AsyncSession=Depends(get_db)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        # user_data = UserResponse(**user)
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            response = await auth_service.create_auth_response(user, finger_print_data, session)
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
    return BaseSuccessResponse(message="Logged out successfully")


@auth_router.post("/refresh")
async def refresh(
    session: AsyncSession=Depends(get_db), 
    refresh_token_data: dict=Depends(RefreshTokenDepends()),
):
    email = refresh_token_data["user"]["email"]
    user = await user_service.get_user_by_email(email, session)
    access_token, _ = create_token(
        user_data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        },
        refresh=False
    )
    response = BaseSuccessResponse(message="Refreshed")
    response.headers["Authorization"] = f"Bearer {access_token}"
    return response
    

@auth_router.post("/current-user")
async def current_user(user: User=Depends(get_current_user)):
    return auth_service.generate_differents_profile(user)
    ...

@auth_router.post("/change-password")
async def current_user(
    passwords: PasswordResetConfirmModel,
    user: User=Depends(get_current_user),
    session: AsyncSession=Depends(get_db), 
):
    await user_service.change_password(passwords.old_password, passwords.new_password, user, session)
    return BaseSuccessResponse(message="Password was changed")




# ADMIN ROUTES

@auth_router.post("/create-new-admin")
async def current_user(
    admin_data: AdminCreateModel,
    session: AsyncSession=Depends(get_db), 
    permission: bool=Depends(RoleChecker([Roles2.admin]))
):
    await auth_service.mail_for_admin(admin_data,session)
    return await auth_service.signup(admin_data, session)
