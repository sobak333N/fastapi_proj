import os
import json
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import app
from app.core.db import get_db, Base


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB")



SQLALCHEMY_TEST_DATABASE_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{TEST_POSTGRES_DB}"
engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


DATA_DIR = Path(__file__).parent / "data"

def load_test_data(path_to_file: str):
    file_path = DATA_DIR / path_to_file
    with open(file_path, "r") as f:
        return json.load(f)


@pytest.fixture
def signup_student_data():
    return load_test_data("auth/signup_student.json")