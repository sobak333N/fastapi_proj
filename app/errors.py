from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError

class CourcesException(Exception):
    """This is the base class for all bookly errors"""

    pass


class InvalidToken(CourcesException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(CourcesException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(CourcesException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(CourcesException):
    """User has provided an access token when a refresh token is needed"""

    pass


class EmailTokenError(CourcesException):
    """Email token has expired or incorrect"""
    pass


class UserAlreadyExists(CourcesException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(CourcesException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(CourcesException):
    """User does not have the neccessary permissions to perform an action."""

    pass


class BookNotFound(CourcesException):
    """Book Not found"""

    pass


class TagNotFound(CourcesException):
    """Tag Not found"""

    pass


class TagAlreadyExists(CourcesException):
    """Tag already exists"""

    pass


class UserNotFound(CourcesException):
    """User Not found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass

def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: CourcesException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        EmailTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid or expired link",
                "resolution": "Please get new link",
                "error_code": "email_token",
            },
        ),
    )
    