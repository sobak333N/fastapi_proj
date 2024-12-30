from fastapi import FastAPI

from app.auth.routes import auth_router
from app.api import (
    category_router,
    course_router,
    instructor_router,
    student_router,
)
from .errors import register_all_errors
from .task_manager import TaskManager
from app.core.mongo_db import init_mongo_db
# from .middleware import register_middleware


version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Ryazanskii Vyacheslav",
        "url": "https://github.com/sobak333N",
        "email": "p.ko1@yandex.com",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_all_errors(app)

# register_middleware(app)
@app.on_event("shutdown")
async def shutdown():
    await TaskManager.wait_for_end()

@app.on_event("startup")
async def startup():
    await init_mongo_db()

app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(category_router, prefix=f"{version_prefix}/category", tags=["category"])
app.include_router(course_router, prefix=f"{version_prefix}/course", tags=["course"])
app.include_router(instructor_router, prefix=f"{version_prefix}/instructor", tags=["instructor"])
app.include_router(student_router, prefix=f"{version_prefix}/student", tags=["student"])


