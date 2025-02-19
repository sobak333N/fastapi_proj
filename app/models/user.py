# models/user.py
from sqlalchemy import (
    Column, Integer, 
    Enum, ForeignKey,
    String, DateTime, 
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.core.db import Base


class Roles2(PyEnum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    second_name = Column(String, nullable=True)
    birthdate = Column(DateTime, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    role = Column(Enum(Roles2))

    student = relationship('Student', back_populates='user', uselist=False) 
    instructor = relationship('Instructor', back_populates='user', uselist=False) 
    refresh_token = relationship('RefreshToken', back_populates='user', lazy='noload') 

    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_user_email', 'email', postgresql_using="hash"),
    )
    primary_key = 'user_id'
