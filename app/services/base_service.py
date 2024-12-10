from typing import Type, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseRepository
from app.errors import InstanceDoesntExists



class BaseService:
    def __init__(self, repository: Type[BaseRepository], model_name: str):
        self.repository = repository()
        self.model_name = model_name

    async def get_instance_by_pk(self, pk: int, session: AsyncSession):
        instance = await self.repository.get_instance_by_pk(pk, session)
        print(instance)
        if instance is None:
            print(self.model_name)
            InstanceDoesntExists(detail=self.model_name)
        return instance

    async def create_instance(self, session: AsyncSession, **kwargs):
        return await self.repository.create_instance(session, **kwargs)
    
    async def update_instance(self, instance: Any, session: AsyncSession, **kwargs):
        return await self.repository.update_instance(instance, session, **kwargs)