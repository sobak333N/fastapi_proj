from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.services.base_service import BaseService
from app.repositories import InstructorRepository, UserRepository
from app.repositories.user import RedisUser
from app.models import User, Instructor
from app.schemas import (
    ShortInstructorResponse, UpdateInstructorResponse, 
    InstructorResponse,
)
from app.errors import InstanceDoesntExists


class InstructorService(BaseService[Instructor]):
    def __init__(self):
        super().__init__(InstructorRepository, "Instructor")
        self.user_repository = UserRepository()

    async def get_instance_by_pk(self, pk: int, session: AsyncSession):
        instructor = await super().get_instance_by_pk(pk, session)
        for attr, value in instructor.user.__dict__.items():
            if not attr.startswith('_'):
                setattr(instructor, attr, value)
        delattr(instructor, 'user')
        return instructor
    
    @RedisUser.del_cache(key_prefix="current_user")
    async def patch_instance(
        self, 
        instructor_model: UpdateInstructorResponse, 
        user: User, 
        session: AsyncSession
    ) -> InstructorResponse:
        excluded_fields = set([
            field for field, value in UpdateInstructorResponse.model_config["fields"].items()
            if value.get("exclude", False) is True 
        ])
        for attr, value in instructor_model.__dict__.items():
            if attr not in excluded_fields:
                if attr in User.__dict__.keys():
                    setattr(user, attr, value)
                if attr in Instructor.__dict__.keys():
                    setattr(user.instructor, attr, value)

        updated_user = await self.user_repository.raw_update_instance(user, session, no_commit=True)
        updated_instructor = await self.repository.raw_update_instance(user.instructor, session, no_commit=True)
        await session.commit()
        updated_user.instructor = updated_instructor 

        for attr, value in updated_user.instructor.__dict__.items():
            if not attr.startswith('_'):
                setattr(updated_user, attr, value)
        return updated_user