# models/instructor.py
from sqlalchemy import (
    Column, Integer, 
    Enum, ForeignKey,
    String, Float, 
    Index
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class AcademicDegree(PyEnum):
    bachelor = "bachelor"
    master = "master"
    doctorate = "doctorate"


class Instructor(Base):
    __tablename__ = 'instructors'
    instructor_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    education = Column(String)
    academic_degree = Column(Enum(AcademicDegree))
    academical_experience = Column(Integer)
    H_index = Column(Float)
    
    profile = relationship('User', back_populates='instructor_profile') 
    course = relationship('Course', back_populates='instructor_course') 

    __table_args__ = (
        Index('idx_instructor_user_id', 'user_id'),
        Index('idx_instructor_instructor_id', 'instructor_id'),
    )