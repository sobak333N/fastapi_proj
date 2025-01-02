from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.user import Roles2
from app.schemas import (
    InputLessonTaskSchema, LessonTaskSchema,
    UpdateLessonTaskSchema
)
from app.core.db import get_db
from app.auth.dependencies import (
    RoleChecker, get_current_user,
)
from app.services import LessonTaskService


lesson_task_router = APIRouter()
lesson_task_service = LessonTaskService()


@lesson_task_router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=LessonTaskSchema)
async def create_lesson_task(
    lesson_model: InputLessonTaskSchema, 
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_task_service.create_instance(user, lesson_model, session)


@lesson_task_router.patch("/update/{lesson_task_id}", status_code=status.HTTP_200_OK, response_model=LessonTaskSchema)
async def update_lesson_task(
    lesson_task_id: int, 
    lesson_mode: UpdateLessonTaskSchema,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_task_service.patch_instance(lesson_task_id, user, lesson_mode, session)


@lesson_task_router.delete("/delete/{lesson_task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_task(
    lesson_task_id: int,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_task_service.delete_instance(lesson_task_id, user, session)