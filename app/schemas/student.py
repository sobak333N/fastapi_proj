from typing import Optional, Any, List

from pydantic import Field, BaseModel 

from app.schemas.user import UserResponse
from app.models.student import SubscriptionPlan, LearningStyle


class StudentResponse(UserResponse):
    student_id: int
    subscription_plan: Optional[SubscriptionPlan] = None
    learning_style: Optional[LearningStyle] = None

    class Config:
        orm_mode = True
        extra = "ignore"


class ShortStudentResponse(StudentResponse):
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
        
        
class UpdateStudentResponse(ShortStudentResponse):

    student_id: Optional[Any] = Field(default=None, exclude=True) 
    created_at: Optional[Any] = Field(default=None, exclude=True)
    role: Optional[Any] = Field(default=None, exclude=True) 

    model_config = {
            "from_attributes": True,
            "orm_mode": True,
            "extra": "ignore",
            "fields": {
                'email': {"exclude": True},
                'user_id': {"exclude": True},
                "student_id": {"exclude": True},
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
                        "learning_style": "visual",
                        "subscription_plan": "free"
                    }
                ]
            },
        }


class LessonStudentAnswer(BaseModel):
    lesson_task_id: int = Field(..., description="lesson_task_id")
    answer: str = Field(..., description="answer")
    

class LessonStudentAnswers(BaseModel):
    answers: List[LessonStudentAnswer] = Field(...)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "answers": [
                    {
                        "lesson_task_id": 315,
                        "answer": "10"
                    },
                    {
                        "lesson_task_id": 316,
                        "answer": "228"
                    },
                ]
                }
            ]
        },
    }

class LessonStudentAnswerResponse(LessonStudentAnswer):
    correct: bool = Field(..., description="correct")


class LessonStudentAnswersResponse(LessonStudentAnswers):
    answers: List[LessonStudentAnswerResponse] = Field(...)
    lesson_id: int = Field(..., description="lesson_id")
    result: int = Field(..., description="result")
    done: bool = Field(..., description="done")
    