import os
import json
from pathlib import Path
import logging
import asyncio

import pytest
from httpx import AsyncClient, Cookies
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from app.core.db import get_db, Base


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# for logger_name in ["sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.dialects"]:
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.WARNING)
#     for handler in logger.handlers[:]:
#         logger.removeHandler(handler)
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
#     logger.addHandler(handler)



# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST")
# TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB")



# SQLALCHEMY_TEST_DATABASE_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{TEST_POSTGRES_DB}"
# engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)
# TestingSessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
# )



# @pytest.fixture(scope="module")
# async def test_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield TestingSessionLocal
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
# @pytest.fixture(scope="function")
def event_loop():
    """
    Создаём общий event loop для всех тестов.
    Это позволяет избежать проблем с передачей Future между разными loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


DATA_DIR = Path(__file__).parent / "data"

def load_test_data(path_to_file: str):
    file_path = DATA_DIR / path_to_file
    with open(file_path, "r") as f:
        return json.load(f)


@pytest.fixture
def signup_student_data():
    return load_test_data("auth/signup_student.json")

@pytest.fixture
def signup_instructor_data():
    return load_test_data("auth/signup_instructor.json")

@pytest.fixture
def credentials():
    return load_test_data("auth/credentials.json")

@pytest.fixture
def passwords():
    return load_test_data("auth/passwords.json")

@pytest.fixture
def create_admin():
    return load_test_data("auth/create_admin.json")



@pytest.fixture
def post_category():
    return load_test_data("category/category_post.json")

@pytest.fixture
def update_category():
    return load_test_data("category/category_update.json")

