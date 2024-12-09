from typing import Optional

from pydantic import Field
from app.schemas.user import UserResponse
from app.models.instructor import AcademicDegree


class InstructorResponse(UserResponse):
    education: str = Field(max_length=30)
    academic_degree: AcademicDegree
    academical_experience: int
    H_index: Optional[float] = None

    class Config:
        orm_mode = True
        extra = "ignore"