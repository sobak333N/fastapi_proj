from typing import Optional

from app.schemas.user import UserResponse
from app.models.student import SubscriptionPlan, LearningStyle

class StudentResponse(UserResponse):
    subscription_plan: Optional[SubscriptionPlan] = None
    learning_style: Optional[LearningStyle] = None

    class Config:
        orm_mode = True
        extra = "ignore"