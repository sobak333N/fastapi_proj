from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.repositories.user import BaseUserRepository
from app.models import Instructor


class InstructorRepository(BaseUserRepository):
    def __init__(self):
        super().__init__(Instructor)
    
    async def get_instance_by_pk(self, pk: int, session: AsyncSession) -> Instructor:
        statement = (
            select(self.model)
            .where(self.model_pk==pk)
            .options(selectinload(self.model.user))
        )
        result = await session.execute(statement)
        instance = result.scalar_one_or_none()
        return instance