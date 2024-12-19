from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.repositories.user import BaseUserRepository
from app.models import Student, StudentCourse


class StudentRepository(BaseUserRepository):
    def __init__(self):
        super().__init__(Student)

    async def get_instance_by_pk(self, pk: int, session: AsyncSession) -> Student:
        statement = (
            select(self.model)
            .where(self.model_pk==pk)
            .options(selectinload(self.model.user))
        )
        result = await session.execute(statement)
        instance = result.scalar_one_or_none()
        return instance

    async def add_to_course(self, session: AsyncSession, **student_course) -> StudentCourse:
        new_instance = StudentCourse(**student_course)
        session.add(new_instance)
        await session.commit()
        return new_instance