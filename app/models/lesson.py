
# models/lesson.py
from typing import List, Union

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import (
    Column, Integer, 
    String, Boolean, 
    ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from beanie import Document

from app.core.db import Base
from app.schemas.other import (
    TextMaterial, ImageMaterial, VideoMaterial, 
    FormulaMaterial, TaskMaterial, SerializeMaterial,
    FullTaskMaterial,
)



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

    @model_validator(mode="after")
    def materials_validator(cls, model):
        model.materials = [
            material if isinstance(material, TaskMaterial)
            else SerializeMaterial.process(material, SerializeMaterial.material_type_dict)
            for material in model.materials
        ]
        return model


class Lesson(Base):
    __tablename__ = 'lessons'
    
    lesson_id = Column(Integer, primary_key=True)
    course_id = Column(
        Integer, ForeignKey('course.course_id', ondelete='CASCADE'), nullable=False
    )

    course = relationship("Course", back_populates="lesson")
    lesson_task = relationship(
        "LessonTask",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

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
