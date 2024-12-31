from enum import Enum as PyEnum
from typing import Union, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, 
    String, Enum, 
    Boolean, ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from beanie import Document

from app.core.db import Base


class TaskTypeEnum(PyEnum):
    test = "Test"
    assignment = "Assignment"


class LessonTaskDocument(Document):
    lesson_task_id: int = Field(..., description="lesson_task_id")
    lesson_id: int = Field(..., description="lesson_id")
    question: str = Field(..., description="question")
    task_type: TaskTypeEnum = Field(..., description="task_type")
    options: Optional[List[str]] = Field(default=None)
    answer: str = Field(..., description="answer")

    class Settings:
        name = "lesson_task"

class LessonTask(Base):
    __tablename__ = 'lesson_tasks'
    
    lesson_task_id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'), nullable=False)

    lesson = relationship("Lesson", back_populates="lesson_task")

    __table_args__ = (
        Index('idx_lesson_tasks_lesson_task_id', 'lesson_task_id'),
        Index('idx_lesson_tasks_lesson_id', 'lesson_id'),
    )
    primary_key = 'lesson_task_id'


class StudentLessonTask(Base):
    __tablename__ = 'student_lesson_task'
    
    student_lesson_task_id = Column(Integer, primary_key=True)
    lesson_task_id = Column(Integer, ForeignKey('lesson_tasks.lesson_task_id'), nullable=False)
    student_lesson_id = Column(Integer, ForeignKey('student_lesson.student_lesson_id'), nullable=False)
    answer = Column(String, nullable=False)
    correct = Column(Boolean, default=False)

    student_lesson = relationship("StudentLesson", back_populates="student_lesson_task")


    __table_args__ = (
        Index('idx_student_lesson_task_lesson_task_id', 'lesson_task_id'),
        Index('idx_student_lesson_task_student_lesson_id', 'student_lesson_id'),
        Index('idx_student_lesson_task_student_lesson_task_id', 'student_lesson_task_id'),
    )
    primary_key = 'student_lesson_task_id'
    
    
    

