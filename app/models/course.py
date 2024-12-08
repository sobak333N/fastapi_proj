# models/course.py
from sqlalchemy import (
    Column, Integer,
    String, DateTime, 
    Enum, ForeignKey, 
    Float, Index,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class Difficulty(PyEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class PaymentType(PyEnum):
    card = "card"
    sbp = "sbp"

class PaymentStatus(PyEnum):
    in_progress = "in_progress"  
    done = "done"  
    pending = "pending"  
    failed = "failed"  
    cancelled = "cancelled"  
    refunded = "refunded"  
    authorized = "authorized"  
    expired = "expired"  
    processing = "processing"  


class Course(Base):
    __tablename__ = 'course'
    course_id = Column(Integer, primary_key=True)
    instructor_id = Column(Integer, ForeignKey('instructors.instructor_id'))
    category_id = Column(Integer, ForeignKey('category.category_id'))

    course_name = Column(String)
    cost = Column(Integer)
    difficulty = Column(Enum(Difficulty))

    category = relationship('Category', back_populates='course') 
    instructor = relationship('Instructor', back_populates='course') 
    lesson = relationship('Lesson', back_populates='course', lazy='noload') 


    __table_args__ = (
        Index('idx_course_course_id', 'course_id'),
        Index('idx_course_instructor_id', 'instructor_id'),
        Index('idx_course_category_id', 'category_id'),
    )


class StudentCourse(Base):
    __tablename__ = 'student_course'
    student_course_id = Column(Integer, primary_key=True)

    course_id = Column(Integer, ForeignKey('course.course_id'))
    student_id = Column(Integer, ForeignKey('students.student_id'))
    payment_type = Column(Enum(PaymentType))
    payment_status = Column(Enum(PaymentStatus))
    progress = Column(Float)
    start_date = Column(DateTime) 
    end_date = Column(DateTime)

    student = relationship('Student', back_populates='course') 
    student_lesson = relationship('StudentLesson', back_populates='student_course') 


    __table_args__ = (
        Index('idx_student_course_student_course_id', 'student_course_id'),
        Index('idx_student_course_course_id', 'course_id'),
        Index('idx_student_course_student_id', 'student_id'),
    )