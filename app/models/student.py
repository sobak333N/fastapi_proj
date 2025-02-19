# models/student.py
from sqlalchemy import (
    Column, Integer, 
    Enum, ForeignKey,
    Index
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class SubscriptionPlan(PyEnum):
    free = "free"
    premium = "premium"
    trial = "trial"

class LearningStyle(PyEnum):
    visual = "visual"
    auditory = "auditory"


class Student(Base):
    __tablename__ = 'students'
    student_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    subscription_plan = Column(Enum(SubscriptionPlan), nullable=False)
    learning_style = Column(Enum(LearningStyle), nullable=True)

    user = relationship('User', back_populates='student') 
    course = relationship('StudentCourse', back_populates='student', lazy='noload') 

    __table_args__ = (
        Index('idx_student_user_id', 'user_id'),
        Index('idx_student_student_id', 'student_id'),
    )
    primary_key = 'student_id'
    