# models/category.py
from sqlalchemy import (
    Column, Integer, 
    String, Index,
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String)
    category_description = Column(String, nullable=True)
    keywords = Column(String, nullable=True)

    course = relationship('Course', back_populates='category')

    __table_args__ = (
        Index('idx_category_category_id', 'category_id'),
    )
    primary_key = 'category_id'