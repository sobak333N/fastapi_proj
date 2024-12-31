from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.services.base_service import BaseService
from app.repositories import LessonRepository
from app.models import User, Lesson
from app.schemas import InputLessonSchema, LessonSchema
from app.services import CourseService

class LessonService(BaseService[Lesson]):
    def __init__(self):
        super().__init__(LessonRepository, "Lesson")
        self.course_service = CourseService()
    
    async def create_instance(
        self, user: User, instance_pydatinc_model: InputLessonSchema, session: AsyncSession
    ) -> Optional[LessonSchema]:
        jsonable_encoded_data = jsonable_encoder(instance_pydatinc_model)
        await self.course_service.handling_valid_instructor(
            jsonable_encoded_data["course_id"], user, session
        )        
        return await self.repository.create_instance(user, session, **jsonable_encoded_data)