from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.user import Roles2
from app.schemas import (
    InputLessonTaskSchema, LessonTaskSchema
)
from app.core.db import get_db
from app.auth.dependencies import (
    RoleChecker, get_current_user,
)
from app.services import LessonTaskService


lesson_task_router = APIRouter()
lesson_task_service = LessonTaskService()


@lesson_task_router.post("create/", status_code=status.HTTP_201_CREATED, response_model=LessonTaskSchema)
async def create_lesson(
    lesson_model: InputLessonTaskSchema, 
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await lesson_task_service.create_instance(user, lesson_model, session)

    