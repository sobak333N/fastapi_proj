# models/category.py
from sqlalchemy import (
    Column, Integer, 
    String, DateTime, 
    Enum, ForeignKey, 
    Index,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base


class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String)

    course = relationship('Course', back_populates='category')
    
    __table_args__ = (
        Index('idx_category_category_id', 'category_id'),
    )