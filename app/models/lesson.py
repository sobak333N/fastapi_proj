# models/lesson.py
from sqlalchemy import (
    Column, Integer, 
    String, Boolean, 
    ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class Lesson(Base):
    __tablename__ = 'lessons'
    
    lesson_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.course_id'), nullable=False)
    lesson_materials = Column(String, nullable=True)

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
    student_course_id = Column(Integer, ForeignKey('student_course.student_course_id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'), nullable=False)
    done = Column(Boolean, default=False)
    result = Column(Integer, nullable=True)

    student_course = relationship("StudentCourse", back_populates="student_lesson")
    student_lesson_task = relationship("StudentLessonTask", back_populates="student_lesson")

    __table_args__ = (
        Index('idx_student_lesson_student_lesson_id', 'student_lesson_id'),
        Index('idx_student_lesson_lesson_id', 'lesson_id'),
        Index('idx_student_lesson_student_course_id', 'student_course_id'),
    )
    primary_key = 'student_lesson_id'
