from typing import List
from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course
from app.services.base_service import BaseService
from app.repositories import CourseRepository
from app.services import CategoryService
from app.errors import InsufficientPermission
from app.base_responses import BaseSuccessResponse


class CourseService(BaseService):
    def __init__(self):
        self.category_service = CategoryService()
        super().__init__(CourseRepository, "Course")
        
    async def create_instance(self, course_pydatinc_model: BaseModel, session: AsyncSession):
        await self.category_service.instance_exists(course_pydatinc_model.category_id, session)
        return await super().create_instance(course_pydatinc_model, session)

    async def patch_instance(self, course_id: int, course_pydatinc_model: BaseModel, session: AsyncSession):
        await self.category_service.instance_exists(course_pydatinc_model.category_id, session)
        instance = await self.get_instance_by_pk(course_id, session)
        if instance.instructor_id != course_pydatinc_model.instructor_id:
            raise InsufficientPermission()
        instance_data = jsonable_encoder(course_pydatinc_model)
        patched_instance = await self.repository.update_instance(instance, session, **instance_data)
        return patched_instance
    
    async def delete_instance(self, instructor_id: int, course_id: int, session: AsyncSession):
        instance = await self.get_instance_by_pk(course_id, session)
        if instance.instructor_id != instructor_id:
            raise InsufficientPermission()
        await self.repository.delete_instance(instance, session)
        return BaseSuccessResponse(message=f"{self.model_name} was deleted")
    
    async def get_all_instance(
        self, 
        page: int, 
        category_ids: List[int] ,
        start_cost: int,
        end_cost: int, 
        session: AsyncSession,
    ) -> List[Course]:
        return await self.repository.get_all_instance(page, category_ids, start_cost, end_cost, session)