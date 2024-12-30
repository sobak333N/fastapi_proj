from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    InputCourseSchema, ShortResponseCourseSchema,
    FullResponseCourseSchema, CoursePagedResponseSchema, 
    PrivateResponseCourseSchema,
)
from app.core.db import get_db
from app.auth.dependencies import (
    RoleChecker, get_current_user,
    not_required_get_current_user,
)

lesson_router = APIRouter()

