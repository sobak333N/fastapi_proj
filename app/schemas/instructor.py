from typing import Optional, Any

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


class UpdateInstructorResponse(ShortInstructorResponse):

    instructor_id: Optional[Any] = Field(default=None, exclude=True) 
    created_at: Optional[Any] = Field(default=None, exclude=True)
    role: Optional[Any] = Field(default=None, exclude=True) 

    model_config = {
            "from_attributes": True,
            "orm_mode": True,
            "extra": "ignore",
            "fields": {
                'email': {"exclude": True},
                'user_id': {"exclude": True},
                "instructor_id": {"exclude": True},
                "created_at": {"exclude": True},
                "role": {"exclude": True},
            },
            "json_schema_extra": {
                "examples": [
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "second_name": "Smith",
                        "birthdate": "2024-12-27",
                        "education": "MSc in Computer Science",
                        "academic_degree": "master",
                        "academical_experience": 5,
                        "H_index": 10,
                    }
                ]
            },
        }
