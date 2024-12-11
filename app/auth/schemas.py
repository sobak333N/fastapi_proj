import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, root_validator

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
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    second_name: Optional[str] = None
    birthdate: Optional[datetime] = None
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    role: Roles2

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


class StudentCreateModel(UserCreateModel):
    subscription_plan: Optional[SubscriptionPlan] = None
    # subscription_plan: Optional[SubscriptionPlan] = None
    learning_style: Optional[LearningStyle] = None

    model_config = student_config

    @root_validator(pre=True)
    def validate_student(cls, values):
        role = values.get("role")
        if role != "student":
            raise ValueError("not student fields")
        return values


class InstructorCreateModel(UserCreateModel):
    education: str = Field(max_length=30)
    academic_degree: AcademicDegree
    academical_experience: int
    H_index: Optional[float] = None

    model_config = instructor_config

    @root_validator(pre=True)
    def validate_instructor(cls, values):
        role = values.get("role")
        if role != "instructor":
            raise ValueError("not instructor fields")
        return values
        

class AdminCreateModel(UserCreateModel):
    @root_validator(pre=True)
    def validate(cls, values):
        email = values.get("email")
        password = values.get("password")
        validate_email(email)
        validate_password(password)
        return values
    
    @root_validator(pre=True)
    def validate_admin(cls, values):
        role = values.get("role")
        if role != "admin":
            raise ValueError("not admin fields")
        return values
        


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)


class PasswordResetRequestModel(BaseModel):
    email: str = Field(max_length=40)

    @root_validator(pre=True)
    def validate(cls, values):
        email = values.get("email")
        validate_email(email)
        return values


class PasswordResetConfirmModel(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @root_validator(pre=True)
    def validate(cls, values):
        new_password = values.get('new_password')
        confirm_new_password = values.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise ValueError("Passwords are not equal")
        validate_password(new_password)
        return values