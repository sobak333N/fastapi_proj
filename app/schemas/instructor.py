from typing import Optional

from pydantic import Field
from app.schemas.user import UserResponse
from app.models.instructor import AcademicDegree


class InstructorResponse(UserResponse):
    instructor_id: int
    education: str = Field(max_length=30)
    academic_degree: AcademicDegree
    academical_experience: int
    H_index: Optional[float] = None

    class Config:
        orm_mode = True
        extra = "ignore"


class ShortInstructorResponse(InstructorResponse):

    user_id: Optional[int] = Field(default=None, exclude=True)
    email: Optional[str] = Field(default=None, exclude=True)

    class Config:
        from_attributes=True
        orm_mode = True
        extra = "ignore"
        fields = {
            'email': 'exclude',
            'user_id': 'exclude',
        }
