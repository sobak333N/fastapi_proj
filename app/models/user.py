# models/user.py
from sqlalchemy import (
    Column, Integer, 
    Enum, ForeignKey,
    String, DateTime, 
    Index
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class Roles(PyEnum):
    active = "student"
    inactive = "instructor"
    admin = "admin"


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    birthdate = Column(DateTime, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    role = Column(Enum(Roles))

    student = relationship('Student', back_populates='user', uselist=False) 
    instructor = relationship('Instructor', back_populates='user', uselist=False) 

    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )