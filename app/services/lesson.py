from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.errors import NotCorrectLessonTasks
from app.services.base_service import BaseService
from app.repositories import LessonRepository, LessonTaskRepository
from app.models import User, Lesson
from app.models.lesson import TaskMaterial
from app.schemas import (
    InputLessonSchema, LessonSchema,
    UpdateLessonSchema,
)
from app.services import CourseService


class LessonService(BaseService[Lesson]):
    def __init__(self):
        super().__init__(LessonRepository, "Lesson")
        self.course_service = CourseService()
        self.lesson_task_repository = LessonTaskRepository()

    async def handling_valid_instructor(
        self, pk: int, user: User, session: AsyncSession
    ) -> Lesson:
        lesson = await self.get_instance_by_pk(pk, session)
        await self.course_service.handling_valid_instructor(
            lesson.course_id, user, session
        )
        return lesson
    
    async def create_instance(
        self, user: User, instance_pydatinc_model: InputLessonSchema, session: AsyncSession
    ) -> Optional[LessonSchema]:
        jsonable_encoded_data = jsonable_encoder(instance_pydatinc_model)
        await self.course_service.handling_valid_instructor(
            jsonable_encoded_data["course_id"], user, session
        )        
        
        return await self.repository.create_instance(session, **jsonable_encoded_data)
    
    async def patch_instance(
        self, pk: int, user: User, instance_pydantic_model: UpdateLessonSchema, session: AsyncSession
    ) -> LessonSchema:
        lesson = await self.handling_valid_instructor(pk, user, session)
        if lesson.course_id != instance_pydantic_model.course_id:
            await self.course_service.handling_valid_instructor(
                instance_pydantic_model.course_id, user, session
            )
        tasks = await self.lesson_task_repository.get_all_tasks_of_lesson(
            lesson, session
        )
        tasks = set([
            task.lesson_task_id for task in tasks
        ])
        input_tasks = set([
            material.lesson_task_id for material in instance_pydantic_model.materials
            if isinstance(material, TaskMaterial)
        ])
        if input_tasks != tasks:
            raise NotCorrectLessonTasks()
        
        jsonable_encoded_data = jsonable_encoder(instance_pydantic_model)
        return await self.repository.update_instance(lesson, session, **jsonable_encoded_data)
        
    async def delete_instance(
        self, pk: int, user: User, session: AsyncSession
    ) -> None:
        lesson = await self.handling_valid_instructor(pk, user, session)
        return await self.repository.delete_instance(lesson, session)
        ...