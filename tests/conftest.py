import os
import json
from pathlib import Path
import logging
import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models import(
    User, Student, Instructor
)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB")

SQLALCHEMY_TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{TEST_POSTGRES_DB}"
engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture
async def get_db_session():
    async with SessionLocal() as session:
        logger.warning("HEEEERRRREEEEE")
        logger.warning(session)
        yield session
        await session.close()

@pytest.fixture
async def clean_tables(get_db_session):
    logger.warning(f"!!!!!reversed(Base.metadata.sorted_tables) = {reversed(Base.metadata.sorted_tables)}")
    for table in reversed(Base.metadata.sorted_tables):
        logger.warning(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE")
        await get_db_session.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))
    await get_db_session.commit()
    logger.warning("CLEEEEAR")

DATA_DIR = Path(__file__).parent / "data"

def load_test_data(path_to_file: str):
    file_path = DATA_DIR / path_to_file
    with open(file_path, "r") as f:
        return json.load(f)

async def apply_inserts(path_to_file, session: AsyncSession):
    logger.critical("APPLIED INSERS")
    sql_script_path = DATA_DIR / path_to_file
    with open(sql_script_path, "r") as file:
        sql_script = file.read()

    sql_statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

    for statement in sql_statements:
        await session.execute(text(statement))
    await session.commit()
    logger.critical("APPLIED INSERS22222")

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

@pytest.fixture
def post_course():
    return load_test_data("course/course_post.json")

@pytest.fixture
def update_course():
    return load_test_data("course/course_update.json")

@pytest.fixture
async def get_course_by_id(get_db_session, clean_tables):
    logger.critical("STARTT")
    logger.critical(get_db_session)  # Должна выводить объект AsyncSession
    test_data = load_test_data("course/course_get_by_id.json")
    database_enviroment_path = test_data["database_enviroment_path"]
    await apply_inserts(database_enviroment_path, get_db_session)
    return test_data
