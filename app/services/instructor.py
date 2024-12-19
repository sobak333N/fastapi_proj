from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.services.base_service import BaseService
from app.repositories import InstructorRepository
from app.schemas import ShortInstructorResponse
from app.errors import InstanceDoesntExists


class InstructorService(BaseService):
    def __init__(self):
        super().__init__(InstructorRepository, "Instructor")

    async def get_instance_by_pk(self, pk: int, session: AsyncSession):
        instructor = await super().get_instance_by_pk(pk, session)
        for attr, value in instructor.user.__dict__.items():
            if not attr.startswith('_'):
                setattr(instructor, attr, value)
        delattr(instructor, 'user')
        return instructor