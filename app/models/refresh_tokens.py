# models/refresh_tokens.py
from sqlalchemy import (
    Column, Integer, 
    Enum, ForeignKey,
    String, Float, 
    Index, BigInteger,
    DateTime,
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.db import Base



class RefreshToken(Base):
    __tablename__ = 'refresh_token'
    refresh_token_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    refresh_token = Column(String, nullable=False)
    finger_print = Column(String, nullable=False )
    expiresIn = Column(BigInteger, nullable=False)

    user = relationship('User', back_populates='refresh_token') 

    __table_args__ = (
        Index('idx_refresh_token_user_id', 'user_id'),
    )
    primary_key = 'refresh_token_id'
