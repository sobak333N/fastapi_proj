from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.repositories import LessonTaskRepository
from app.schemas import InputLessonTaskSchema, LessonTaskSchema
from app.models import User, LessonTask
from app.services import LessonService, CourseService


class LessonTaskService(BaseService[LessonTask]):
    def __init__(self):
        super().__init__(LessonTaskRepository, "LessonTask")
        self.lesson_service = LessonService()
        self.course_service = CourseService()
        
        
    async def create_instance(
        self, user: User, instance_pydatinc_model: InputLessonTaskSchema, session: AsyncSession
    ) -> LessonTaskSchema:
        lesson = await self.lesson_service.get_instance_by_pk(
            instance_pydatinc_model.lesson_id, session
        )
        await self.course_service.handling_valid_instructor(
            lesson.course_id,  
        )
        ...