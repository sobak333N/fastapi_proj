import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, root_validator

from app.models.user import Roles2
from app.auth.utils import validate_password, validate_email


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    role: Roles2

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe123@co.com",
                "password": "testpass123",
                "role": "instructor",
            }
        }
    }

    @root_validator(pre=True)
    def validate(cls, values):
        role = values.get("role")
        email = values.get("email")
        password = values.get("password")
        if role == "admin":
            raise ValueError("Error")
        validate_email(email)
        validate_password(password)
        return values


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=12)


class PasswordResetRequestModel(BaseModel):
    email: str = Field(max_length=40)

    @root_validator(pre=True)
    def validate(cls, values):
        email = values.get("email")
        validate_email(email)
        return values

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

    @root_validator(pre=True)
    def validate(cls, values):
        new_password = values.get('new_password')
        confirm_new_password = values.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise ValueError("Passwords are not equal")
        email = values.get("email")
        validate_email(email)
        return values