from typing import Any, List, Tuple, Type, Optional
from datetime import datetime, timedelta

from fastapi import Depends, Request, status

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User, Roles2
# from src.db.redis import token_in_blocklist

from app.services.user import UserService
from app.models import User
from app.auth.schemas import UserCreateModel, StudentCreateModel, InstructorCreateModel
from app.repositories.user import UserRepository
from app.auth.utils import decode_token
from app.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
)

user_service = UserService()
user_repository = UserRepository()


class AccessTokenDepends(HTTPBearer):
    def __init__(self, auto_error: bool=True, required_auth: bool=True):
        self.required_auth = required_auth
        return super().__init__(auto_error=auto_error)
    
    async def __call__(
        self, 
        request: Request,
    ) -> Optional[HTTPAuthorizationCredentials]:
        creds = await super().__call__(request)
        if not creds:
            return None
        token = creds.credentials
        token_data = decode_token(token)
        if token_data is None:
            return None if self.required_auth else self._raise_access_token_required()

        #  redis check jti
        token_in_blocklist = await user_service.token_in_blocklist(token_data["jti"])
        if token_in_blocklist:
            return None if self.required_auth else self._raise_access_token_required()
        if token_data["refresh"] is True:
            return None if self.required_auth else self._raise_access_token_required()
        if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
            return None if self.required_auth else self._raise_access_token_required()
        return token_data

    def _raise_access_token_required(self):
        raise AccessTokenRequired()


class RefreshTokenDepends:
    def __init__(self):
        pass

    async def __call__(self, 
        request: Request,
        session: AsyncSession = Depends(get_db),
    ) -> dict | None:
        token = request.cookies.get("refresh_token")
        if not token:
            raise RefreshTokenRequired()
        token_data = decode_token(token)
        if not token_data:
            raise RefreshTokenRequired()

        print(token_data)
        print(token)

#       validate token in db
        refresh_token_in_whitelist = await user_repository.refresh_token_exists(token, session)
        if not refresh_token_in_whitelist:
            raise RefreshTokenRequired()

        if token_data["refresh"] is False:
            raise RefreshTokenRequired()
        if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
            raise RefreshTokenRequired()
        
        token_data["token"] = token
        return token_data


async def get_current_user(
    token_details: dict = Depends(AccessTokenDepends()),
    session: AsyncSession = Depends(get_db),
):    
    user_email = token_details["user"]["email"]
    user = await user_repository.get_user_by_email(user_email, session)
    return user


async def not_required_get_current_user(
    token_details: dict = Depends(AccessTokenDepends(auto_error=False, required_auth=False)),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:    
    if not token_details:
        return None
    user_email = token_details["user"]["email"]
    user = await user_repository.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = set(allowed_roles)

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()

