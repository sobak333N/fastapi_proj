from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError

class CourcesException(HTTPException):
    """This is the base class for all Cources errors"""
    
    def __init__(self, status_code: int = None, detail: str = None, **kwargs):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail, **kwargs)

class InvalidToken(CourcesException):
    """User has provided an invalid or expired token"""
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
    """User does not have the necessary permissions to perform an action."""
    pass


class InstanceDoesntExists(CourcesException):
    """Instance doesn't exist error."""
    
    def __init__(self, detail: str = "Instance with this id doesn't exist", **kwargs):
        # Use model_name for dynamic message replacement
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, **kwargs)


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: CourcesException):
        print(exc)
        if hasattr(exc, "detail"):
            # If the exception has a model name, modify the message accordingly
            if hasattr(exc, 'model_name') and exc.model_name:
                initial_detail["message"] = initial_detail["message"].replace("Instance", exc.model_name)
        return JSONResponse(status_code=status_code, content=initial_detail)

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
                "message": "Token is invalid or expired",
                "resolution": "Please get a new token",
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
                "resolution": "Please get a refresh token",
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
                "resolution": "Please get a new link",
                "error_code": "email_token",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid credentials",
                "resolution": "Please input valid credentials",
                "error_code": "invalid_credentials",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "This route is forbidden for you",
                "error_code": "forbidden",
                "resolution": "...",
            },
        ),
    )
    app.add_exception_handler(
        InstanceDoesntExists,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Instance with this id doesn't exist",
                "resolution": "Please check the entity identifier and try again",
                "error_code": "not_found",
            },
        ),
    )
