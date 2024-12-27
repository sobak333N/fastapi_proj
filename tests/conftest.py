import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import asyncio

import pytest
from httpx import AsyncClient, Cookies
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

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



POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB")



SQLALCHEMY_TEST_DATABASE_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{TEST_POSTGRES_DB}"
engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)



# @pytest.fixture(scope="function")
@asynccontextmanager
async def create_enviroment():
    async with TestingSessionLocal() as session:
        # await session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
        # await session.begin()

        tables_query = """
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename != 'alembic_version';
        """
        result = await session.execute(text(tables_query))
        tables = [row[0] for row in result.fetchall()]

        for table in tables:
            await session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'))


        sequence_reset_query = """
            DO $$
            DECLARE
                seq RECORD;
            BEGIN
                FOR seq IN 
                    SELECT c.relname AS sequence_name
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'S' AND n.nspname = 'public'  -- Only sequences in the 'public' schema
                LOOP
                    EXECUTE format('SELECT setval(''public.%I'', 1, false);', seq.sequence_name);
                END LOOP;
            END;
            $$;
        """
        await session.execute(text(sequence_reset_query))

        logger.critical("AAAALLLL GOOD MAN")
        try:
            yield session
        finally:
            await session.rollback()


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


async def apply_inserts(path_to_file, session):
    logger.critical("APPLIED INSERS")
    sql_script_path = DATA_DIR / path_to_file
    with open(sql_script_path, "r") as file:
        sql_script = file.read()

    sql_statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

    for statement in sql_statements:
        await session.execute(text(statement))
    res = await session.execute(text("SELECT * FROM users"))
    res = res.scalars().all()
    logger.critical(f"{res=}")
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
async def get_course_by_id():
    logger.critical("STARTT")
    test_data = load_test_data("course/course_get_by_id.json")
    database_enviroment_path = test_data["database_enviroment_path"]
    async with create_enviroment() as session:
        await apply_inserts(database_enviroment_path, session)
    return test_data