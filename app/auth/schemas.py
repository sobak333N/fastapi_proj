import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import (
    BaseModel, Field, ValidationError,
    field_validator, model_validator
)
from pydantic_core import PydanticCustomError

from app.models.user import Roles2
from app.models.student import SubscriptionPlan, LearningStyle
from app.models.instructor import AcademicDegree
from app.auth.utils import validate_password, validate_email

# EXAMPLES:
instructor_config = {
    "json_schema_extra": {
        "example": {
            "first_name": "John",
            "last_name": "Doe",
            "second_name": "Gondoe",
            "birthdate": "2004-08-06",
            "email": "johndoe123@co.com",
            "password": "Q1w2e3r4-",
            "role": "instructor",
            "education": "MIFI",
            "academic_degree": "master",
            "academical_experience": 10,
            "H_index": 4.0,
        }
    }
}
student_config = {
    "json_schema_extra": {
        "example": {
            "first_name": "John",
            "last_name": "Doe",
            "second_name": "Gondoe",
            "birthdate": "2004-08-06",
            "email": "johndoe123@co.com",
            "password": "Q1w2e3r4-",
            "role": "student",
            "subscription_plan": "free",
            "learning_style": "visual",
        }
    }
}
admin_config = {
    "json_schema_extra": {
        "example": {
            "first_name": "John",
            "last_name": "Doe",
            "second_name": "Gondoe",
            "birthdate": "2004-08-06",
            "email": "admin@co.com",
            "password": "Q1w2e3r4-",
            "role": "admin",
        }
    }
}

class UserCreateModel(BaseModel):
    first_name: str = Field(min_length=1, max_length=25)
    last_name: str = Field(min_length=1, max_length=25)
    second_name: Optional[str] = None
    birthdate: Optional[datetime] = None
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=128)
    role: Roles2

    @field_validator("first_name", "last_name")
    def validate_non_empty(cls, value: str, info):
        if not value.strip():
            raise PydanticCustomError(
                f"value_error.non_empty",
                f"{info.field_name} cannot be empty or only whitespace", 
                {"input": value, "expected": "non empty"}
            )

    @field_validator("role")
    def validate_role(cls, role: str):
        if role == "admin":
            raise PydanticCustomError(
                "value_error.role",
                "Role admin is not allowed", 
                {"input": role, "expected": "student|instructor"}
            )
        return role

    @field_validator("email")
    def validate_email(cls, email: str):
        validate_email(email)
        return email

    @field_validator("password")
    def validate_password(cls, password: str):
        validate_password(password)
        return password


class StudentCreateModel(UserCreateModel):
    subscription_plan: Optional[SubscriptionPlan] = None
    learning_style: Optional[LearningStyle] = None

    model_config = student_config

    @field_validator("role")
    def validate_student_role(cls, role: Roles2):
        if role != Roles2.student:
            raise PydanticCustomError(
                "value_error.role",
                "Role must be 'student'", 
                {"input": role, "expected": "student"}
            )
        return role 


class InstructorCreateModel(UserCreateModel):
    education: str = Field(min_length=1, max_length=30)
    academic_degree: AcademicDegree
    academical_experience: int = Field(gt=0)
    H_index: Optional[float] = None

    model_config = instructor_config

    @field_validator("H_index")
    def validate_H_index(cls, H_index: str):
        if H_index and H_index < 0:
            raise PydanticCustomError(
                "value_error.H_index",
                "H_index should be greater than 0", 
                {"input": H_index, "expected": "greater than 0"}
            )
        return H_index 

    @field_validator("role")
    def validate_instructor_role(cls, role: str):
        if role != Roles2.instructor:
            raise PydanticCustomError(
                "value_error.role",
                "Role must be 'instructor'", 
                {"input": role, "expected": "instructor"}
            )
        return role 


class AdminCreateModel(UserCreateModel):

    @field_validator("role")
    def validate_admin_role(cls, role: str):
        if role != Roles2.admin:
            raise PydanticCustomError(
                "value_error.role",
                "Role must be 'admin'", 
                {"input": role, "expected": "admin"}
            )
        return role 
        


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)


class PasswordResetRequestModel(BaseModel):
    email: str = Field(max_length=40)

    @field_validator("email")
    def validate_email(cls, email: str):
        validate_email(email)
        return email


class PasswordResetConfirmModel(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @model_validator(mode="after")
    def validate_passwords(cls, values):
        new_password = values.new_password
        confirm_new_password = values.confirm_new_password

        if new_password != confirm_new_password:
            raise ValueError("Passwords are not equal")

        validate_password(new_password)
        return values
    