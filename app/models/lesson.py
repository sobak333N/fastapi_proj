
# models/lesson.py
from typing import List, Union
from enum import Enum as PyEnum

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, 
    String, Boolean, 
    ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from beanie import Document

from app.core.db import Base


class MaterialType(PyEnum):
    text = "text"
    image = "image"
    video = "video"
    formula = "formula"
    lesson_task = "task"


class BaseMaterial(BaseModel):
    type: MaterialType = Field(..., description="Тип материала") 


class TextMaterial(BaseMaterial):
    type: MaterialType = MaterialType.text
    data: str = Field(..., description="Текст материала")


class ImageMaterial(BaseMaterial):
    type: MaterialType = MaterialType.image
    data: str = Field(..., description="Ссылка на изображение")


class VideoMaterial(BaseMaterial):
    type: MaterialType = MaterialType.video
    data: str = Field(..., description="Ссылка на видео")


class FormulaMaterial(BaseMaterial):
    type: MaterialType = MaterialType.formula
    data: str = Field(..., description="Формула в LaTeX формате")


class TaskMaterial(BaseMaterial):
    type: MaterialType = MaterialType.lesson_task
    lesson_task_id: int = Field(..., description="ID задачи из MongoDB")


class LessonDocument(Document):
    lesson_id: int
    lesson_name: str
    materials: List[
        Union[TextMaterial, ImageMaterial, VideoMaterial, FormulaMaterial, TaskMaterial]
    ] = Field(
        default=[],
        description="Материалы урока"
    )
    
    class Settings:
        name = "lesson"


class Lesson(Base):
    __tablename__ = 'lessons'
    
    lesson_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.course_id'), nullable=False)

    course = relationship("Course", back_populates="lesson")
    lesson_task = relationship("LessonTask", back_populates="lesson")

    __table_args__ = (
        Index('idx_lessons_lesson_id', 'lesson_id'),
        Index('idx_lessons_course_id', 'course_id'),
    )
    primary_key = 'lesson_id'



class StudentLesson(Base):
    __tablename__ = 'student_lesson'
    
    student_lesson_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.student_id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'), nullable=False)
    done = Column(Boolean, default=False)
    result = Column(Integer, nullable=True)

    student_lesson_task = relationship("StudentLessonTask", back_populates="student_lesson")

    __table_args__ = (
        Index('idx_student_lesson_student_lesson_id', 'student_lesson_id'),
        Index('idx_student_lesson_lesson_id', 'lesson_id'),
        Index('idx_student_lesson_student_id', 'student_id'),
    )
    primary_key = 'student_lesson_id'
