from typing import List, Optional
from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, User
from app.models.user import Roles2
from app.services.base_service import BaseService
from app.repositories import CourseRepository
from app.services import CategoryService
from app.errors import InsufficientPermission
from app.base_responses import BaseSuccessResponse


class CourseService(BaseService[Course]):
    def __init__(self):
        self.category_service = CategoryService()
        super().__init__(CourseRepository, "Course")
        
    async def create_instance(self, course_pydatinc_model: BaseModel, session: AsyncSession):
        await self.category_service.instance_exists(course_pydatinc_model.category_id, session)
        return await super().create_instance(course_pydatinc_model, session)

    async def handling_valid_instructor(self, course_id: int, user: User, session: AsyncSession) -> Optional[Course]:
        instance = await super().get_instance_by_pk(course_id, session)
        if instance.instructor_id != user.instructor.instructor_id:
            raise InsufficientPermission()
        return instance

    async def patch_instance(self, course_id: int, user: User, course_pydatinc_model: BaseModel, session: AsyncSession):
        await self.category_service.instance_exists(course_pydatinc_model.category_id, session)
        instance = await self.handling_valid_instructor(course_id, user, session)
        instance_data = jsonable_encoder(course_pydatinc_model)
        patched_instance = await self.repository.update_instance(instance, session, **instance_data)
        return patched_instance
    
    async def delete_instance(self, user: User, course_id: int, session: AsyncSession):
        instance = await self.handling_valid_instructor(course_id, user, session)
        await self.repository.delete_instance(instance, session)
        return BaseSuccessResponse(message=f"{self.model_name} was deleted")
    
    async def get_all_instance(
        self, 
        page: int, 
        category_ids: List[int],
        start_cost: int,
        end_cost: int, 
        session: AsyncSession,
    ) -> List[Course]:
        return await self.repository.get_all_instance(page, category_ids, start_cost, end_cost, session)

    async def instance_exists(self, pk: int, session: AsyncSession) -> bool:
        return bool(await super().get_instance_by_pk(pk, session))

    async def get_instance_by_pk(self, pk: int, user: User, session: AsyncSession):
        course = await super().get_instance_by_pk(pk, session)
        access = await self.check_access_to_course(course, user, session)
        if not access:
            delattr(course, 'private_info')
        return course
    
    async def check_access_to_course(self, course: Course, user: User, session: AsyncSession) -> bool:
        if user:
            if user.role == Roles2.instructor:
                if course.instructor_id != user.instructor.instructor_id:
                    return False
            elif user.role == Roles2.student:
                student_access = await self.repository.check_access_of_user(
                    course_id=course.course_id, 
                    student_id=user.student.student_id, 
                    session=session,
                )
                if not student_access: 
                    return False
            return True
        return False