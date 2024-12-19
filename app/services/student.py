import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.repositories import StudentRepository, CourseRepository
from app.models.course import PaymentType, PaymentStatus
from app.models import Course
from app.base_responses import BaseSuccessResponse
from app.services import CourseService


class StudentService(BaseService):
    def __init__(self):
        super().__init__(StudentRepository, "Student")
        self.course_service = CourseService()

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