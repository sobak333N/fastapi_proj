from typing import Any, List
from datetime import datetime, timedelta

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User
# from src.db.redis import token_in_blocklist

from app.services.user import UserService
from app.repositories.user import UserRepository
from app.auth.utils import decode_token
from app.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
)

user_service = UserService()
user_repository = UserRepository()

class AccessTokenDepends(HTTPBearer):
    def __init__(self, auto_error=True):
        return super().__init__(self, auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if token_data is None:
            raise InvalidToken()
        # if token_data[]
        #  redis check jti
        if token_data["refresh"] is True:
            raise AccessTokenRequired()
        if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
            raise AccessTokenRequired()
        return token_data


class RefreshTokenDepends:
    def __init__(self):
        pass

    async def __call__(self, request: Request) -> dict | None:
        token = request.cookies.get("refresh_token")
        if not token:
            raise RefreshTokenRequired()
        token_data = decode_token(token)
        if not token_data:
            raise RefreshTokenRequired()
        
        if token_data["refresh"] is False:
            raise RefreshTokenRequired()
        if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
            raise RefreshTokenRequired()
        
#       validate token in db 
        
        return token_data


async def get_current_user(
    token_details: dict = Depends(AccessTokenDepends()),
    session: AsyncSession = Depends(get_db),
):
    user_email = token_details["user"]["email"]
    user = await user_repository.get_user_by_email(user_email, session)
    return user


# class RoleChecker:
#     def __init__(self, allowed_roles: List[str]) -> None:
#         self.allowed_roles = allowed_roles

#     def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
#         if not current_user.is_verified:
#             raise AccountNotVerified()
#         if current_user.role in self.allowed_roles:
#             return True

#         raise InsufficientPermission()
