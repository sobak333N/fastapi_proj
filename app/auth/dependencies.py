from typing import Any, List, Tuple, Type, Optional
from datetime import datetime, timedelta

from fastapi import Depends, Request, status

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User, Roles2
from app.models import Instructor
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


class FingerPrint:
    def __init__(self):
        pass

    def __call__(
        self, 
        request: Request,
    ) -> Optional[dict]:
        client_ip =request.client.host
        forwarded_ip =request.headers.get("x-forwarded-for")
        real_ip =request.headers.get("x-real-ip")
        ip = forwarded_ip if forwarded_ip else real_ip

        user_agent = request.headers.get("user-agent")

        return {"user_agent": user_agent, "ip": ip}


class AccessTokenDependsForRequirement(HTTPBearer):
    def __init__(self, auto_error: bool=True):
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
        await self.__validate_access_token(token_data)
        return token_data

    async def __validate_access_token(self, token_data):
        if token_data is None:
            return self._raise_access_token_required()
        #  redis check jti
        token_in_blocklist = await user_service.token_in_blocklist(token_data["jti"])
        if token_in_blocklist:
            return self._raise_access_token_required()
        if token_data["refresh"] is True:
            return self._raise_access_token_required()
        if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
            return self._raise_access_token_required()

    def _raise_access_token_required(self):
        raise AccessTokenRequired()
    

class AccessTokenDependsForNotRequired(HTTPBearer):
    def __init__(self, auto_error: bool=True):
        self.required_auth = required_auth
        return super().__init__(auto_error=auto_error)
    
    async def __call__(
        self,
        request: Request,
    ) -> Optional[HTTPAuthorizationCredentials]:
        return None


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
    token_details: dict = Depends(AccessTokenDependsForNotRequired())),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:    
    try:
        token_details: dict = Depends(AccessTokenDepends(auto_error=False, required_auth=False)),
    except AccessTokenRequired:
        return None
    # if not token_details:
    #     return None
    user_email = token_details["user"]["email"]
    user = await user_repository.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = set(allowed_roles)

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        # print(current_user.role)
        # print(self.allowed_roles)
        if current_user.role in self.allowed_roles or current_user.role in set(map(lambda x: x.value, self.allowed_roles)):
            return True

        raise InsufficientPermission()

