from sqlalchemy import (
    Column, Integer, 
    String, Enum, 
    Boolean, ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class TaskTypeEnum(PyEnum):
    TEST = "Test"
    ASSIGNMENT = "Assignment"


class LessonTask(Base):
    __tablename__ = 'lesson_tasks'
    
    lesson_task_id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'), nullable=False)
    question = Column(String, nullable=False)
    task_type = Column(Enum(TaskTypeEnum), nullable=False)
    answers = Column(String, nullable=True)  # Could be JSON or a serialized list of answers
    answer = Column(String, nullable=False)

    lesson = relationship("Lesson", back_populates="lesson_tasks")

    __table_args__ = (
        Index('idx_lesson_tasks_lesson_task_id', 'lesson_task_id'),
        Index('idx_lesson_tasks_lesson_id', 'lesson_id'),
    )

class StudentLessonTask(Base):
    __tablename__ = 'student_lesson_task'
    
    student_lesson_task_id = Column(Integer, primary_key=True)
    lesson_task_id = Column(Integer, ForeignKey('lesson_tasks.lesson_task_id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False)
    answer = Column(String, nullable=False)
    correct = Column(Boolean, default=False)

    lesson_task = relationship("LessonTask", back_populates="student_answers")
    student = relationship("Student", back_populates="lesson_task_answers")

    __table_args__ = (
        Index('idx_student_lesson_task_lesson_task_id', 'lesson_task_id'),
    )