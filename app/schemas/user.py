from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic.networks import EmailStr

class RolesEnum(str, Enum):
    student = 'student'
    instructor = 'instructor'
    admin = 'admin' 


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    second_name: Optional[str] = None
    birthdate: Optional[datetime] = None
    created_at: datetime
    role: RolesEnum

    class Config:
        orm_mode = True
        extra = "ignore"