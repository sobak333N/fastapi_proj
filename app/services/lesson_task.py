from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.services.base_service import BaseService
from app.repositories import LessonTaskRepository
from app.schemas import (
    InputLessonTaskSchema, LessonTaskSchema,
    UpdateLessonTaskSchema,
)
from app.models import User, LessonTask, Lesson
from app.services import LessonService, CourseService


class LessonTaskService(BaseService[LessonTask]):
    def __init__(self):
        super().__init__(LessonTaskRepository, "LessonTask")
        self.lesson_service = LessonService()
        self.course_service = CourseService()

    async def handling_valid_instructor(
        self, pk: int, user: User, session: AsyncSession
    ) -> Tuple[LessonTask, Lesson]:
        lesson_task = await self.get_instance_by_pk(pk, session)
        lesson = await self.lesson_service.handling_valid_instructor(
            lesson_task.lesson_id, user, session
        )
        return lesson_task, lesson
    
    async def create_instance(
        self, user: User, instance_pydatinc_model: InputLessonTaskSchema, session: AsyncSession
    ) -> LessonTaskSchema:
        lesson = await self.lesson_service.get_instance_by_pk(
            instance_pydatinc_model.lesson_id, session
        )
        await self.course_service.handling_valid_instructor(
            lesson.course_id, user, session
        )
        jsonable_encoded_data = jsonable_encoder(instance_pydatinc_model)
        return await self.repository.create_instance(session, **jsonable_encoded_data)
    
    async def patch_instance(
        self, pk: int, user: User, instance_pydantic_model: UpdateLessonTaskSchema, session: AsyncSession
    ) -> LessonTaskSchema:
        lesson_task, lesson = await self.handling_valid_instructor(pk, user, session)
        if lesson.lesson_id != instance_pydantic_model.lesson_id:
            new_lesson = await self.lesson_service.get_instance_by_pk(
                instance_pydantic_model.lesson_id, session
            )
            await self.course_service.handling_valid_instructor(
                new_lesson.course_id, user, session
            )
        jsonable_encoded_data = jsonable_encoder(instance_pydantic_model)
        return await self.repository.update_instance(lesson_task, session, **jsonable_encoded_data)
    
    async def delete_instance(
        self, pk: int, user: User, session: AsyncSession
    ) -> None:
        lesson_task, lesson = await self.handling_valid_instructor(pk, user, session)
        return await self.repository.delete_instance(lesson_task, session)