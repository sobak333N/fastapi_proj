from typing import List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from beanie.operators import In

from .base_repository import BaseRepository
from app.models import (
    Course, User, StudentCourse,
    Lesson, LessonDocument, LessonTaskDocument,
)
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
        course_id: int, 
        student_id: int,
        session: AsyncSession,
    ) -> bool:
        statement = (
            select(StudentCourse)
            .where(StudentCourse.student_id==student_id)
            .where(StudentCourse.course_id==course_id)
        )
        result = await session.execute(statement)
        result = result.scalars().first()
        if not result or result.payment_status != PaymentStatus.done:
            return False
        return True
    
    async def delete_instance(
        self, instance: Course, session: AsyncSession, no_commit: bool=False
    ) -> None:
        statement = (
            select(Lesson.lesson_id)
            .where(Lesson.course_id == instance.course_id)
        )
        lessons = await session.execute(statement)
        lesson_ids = [row.lesson_id for row in lessons.fetchall()]

        await LessonDocument.find(
            In(LessonDocument.lesson_id, lesson_ids)
        ).delete_many()
        await LessonTaskDocument.find(
            In(LessonTaskDocument.lesson_id, lesson_ids)
        ).delete_many()

        return await super().delete_instance(instance, session, no_commit)
