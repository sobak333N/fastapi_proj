from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.user import Roles2
from app.schemas import (
    InputLessonSchema, LessonSchema,
    UpdateLessonSchema
)
from app.core.db import get_db
from app.auth.dependencies import (
    RoleChecker, get_current_user,
    not_required_get_current_user,
)
from app.services import LessonService


lesson_router = APIRouter()
lesson_service = LessonService()


@lesson_router.post("create/", status_code=status.HTTP_201_CREATED, response_model=LessonSchema)
async def create_lesson(
    lesson_model: InputLessonSchema, 
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_service.create_instance(user, lesson_model, session)


@lesson_router.patch("update/{lesson_id}", status_code=status.HTTP_200_OK, response_model=LessonSchema)
async def update_lesson(
    lesson_id: int,
    lesson_model: UpdateLessonSchema,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_service.patch_instance(lesson_id, user, lesson_model, session)
    ...