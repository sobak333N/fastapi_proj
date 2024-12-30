import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import Config
from app.models import LessonDocument, LessonTaskDocument


Base = declarative_base()

engine = create_async_engine(Config.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def init_mongo_db():
    client = AsyncIOMotorClient(Config.MONGO_DB_URL)
    await init_beanie(
        database=client[Config.MONGO_DB], 
        document_models=[LessonDocument, LessonTaskDocument]
    )
