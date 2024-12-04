import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db():
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


@asynccontextmanager
async def get_transaction_db():
    session: AsyncSession = SessionLocal()
    try:
        await session.begin()
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.commit()
        await session.close()