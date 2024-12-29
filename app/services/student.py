from typing import Any
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.repositories import StudentRepository, CourseRepository
from app.repositories.user import RedisUser, UserRepository
from app.models.course import PaymentType, PaymentStatus
from app.models import Course, User, Student
from app.schemas import UpdateStudentResponse
from app.base_responses import BaseSuccessResponse
from app.services import CourseService


class StudentService(BaseService):
    def __init__(self):
        super().__init__(StudentRepository, "Student")
        self.course_service = CourseService()
        self.user_repository = UserRepository()

    async def get_instance_by_pk(self, pk: int, session: AsyncSession):
        student = await super().get_instance_by_pk(pk, session)
        for attr, value in student.user.__dict__.items():
            if not attr.startswith('_'):
                setattr(student, attr, value)
        delattr(student, 'user')
        return student
    
    async def buy_course(
        self, 
        course_id: int, 
        student_id: int, 
        payment_type: PaymentType,
        session: AsyncSession,
    ) -> BaseSuccessResponse:

        # checking existing of course
        await self.course_service.get_instance_by_pk(pk=course_id, session=session)
        
        # background task with sending request to external financial service
        # asyncio.create_task()

        data = {
            "course_id": course_id,
            "student_id": student_id,
            "payment_type": payment_type,
            "payment_status": PaymentStatus.in_progress
        }
        await self.repository.add_to_course(session, **data)
        return BaseSuccessResponse("Waiting for processing for your payment")
    
    @RedisUser.del_cache(key_prefix="current_user")
    async def patch_instance(
        self, 
        student_model: UpdateStudentResponse, 
        user: User, 
        session: AsyncSession
    ) -> Any:
        excluded_fields = set([
            field for field, value in UpdateStudentResponse.model_config["fields"].items()
            if value.get("exclude", False) is True 
        ])
        for attr, value in student_model.__dict__.items():
            if attr not in excluded_fields:
                if attr in User.__dict__.keys():
                    setattr(user, attr, value)
                if attr in Student.__dict__.keys():
                    setattr(user.student, attr, value)

        updated_user = await self.user_repository.raw_update_instance(user, session, no_commit=True)
        updated_student = await self.repository.raw_update_instance(user.student, session, no_commit=True)
        await session.commit()
        updated_user.student = updated_student 

        for attr, value in updated_user.student.__dict__.items():
            if not attr.startswith('_'):
                setattr(updated_user, attr, value)
        return updated_user