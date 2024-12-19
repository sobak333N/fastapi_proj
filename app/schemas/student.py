from typing import Optional

from pydantic import Field
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