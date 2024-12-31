from typing import List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from app.models import Course, User, StudentCourse
from app.models.course import PaymentStatus
from app.config import Config


class CourseRepository(BaseRepository[Course]):
    def __init__(self):
        super().__init__(Course)
    
    async def get_all_instance(
        self, 
        page: int, 
        category_ids: List[int] ,
        start_cost: int,
        end_cost: int, 
        session: AsyncSession,
    ) -> List[Course]:
        statement = (
            select(Course)
            .filter(Course.category_id.in_(category_ids))
            .filter(Course.cost.between(start_cost, end_cost))
            .order_by(Course.course_id)
            .offset(Config.PAGE_LIMIT*(page-1))
            .limit(Config.PAGE_LIMIT)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def check_access_of_user(
        self,
        course: Course, 
        student_id: int,
        session: AsyncSession,
    ) -> bool:
        statement = (
            select(StudentCourse)
            .where(StudentCourse.student_id==student_id)
            .where(StudentCourse.course_id==course.course_id)
        )
        result = await session.execute(statement)
        result = result.scalars().first()
        if not result or result.payment_status != PaymentStatus.done:
            return False
        return True
        