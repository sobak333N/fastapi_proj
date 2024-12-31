from typing import (
    Type, Any, Tuple, 
    TypeVar, Optional, List,
    Generic,
)
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.repositories.base_repository import BaseRepository
from app.errors import InstanceDoesntExists
from app.base_responses import BaseSuccessResponse


T = TypeVar('T')


class BaseService(Generic[T]):
    def __init__(self, repository: Type[BaseRepository], model_name: str):
        self.repository = repository()
        self.model_name = model_name

    async def get_instance_by_pk(self, pk: int, session: AsyncSession) -> Optional[T]:
        instance = await self.repository.get_instance_by_pk(pk, session)
        if instance is None:
            raise InstanceDoesntExists(message=self.model_name)
        return instance

    # async def get_instance_by_unique_field(self, pk: int, session: AsyncSession):
    #     instance = await self.repository.get_instance_by_pk(pk, session)
    #     if instance is None:
    #         raise InstanceDoesntExists(message=self.model_name)
    #     return instance
    
    async def instance_exists(self, pk: int, session: AsyncSession) -> bool:
        return bool(await self.get_instance_by_pk(pk, session))

    async def get_all_instance(self, page: int, session: AsyncSession) -> List[T]:
        return await self.repository.get_all_instance(page, session)

    async def get_total_count(self, session) -> int:
        return await self.repository.get_total_count(session)

    async def create_instance(
        self, instance_pydatinc_model: BaseModel, session: AsyncSession
    ) -> T:
        instance_data = jsonable_encoder(instance_pydatinc_model)
        return await self.repository.create_instance(session, **instance_data)
    
    async def update_instance(
        self, instance: Any, instance_pydatinc_model: BaseModel, session: AsyncSession
    ) -> T:
        instance_data = jsonable_encoder(instance_pydatinc_model)
        return await self.repository.update_instance(instance, session, **instance_data)
    
    async def delete_instance(self, pk: int, session: AsyncSession) -> None:
        instance = await self.get_instance_by_pk(pk, session)
        await self.repository.delete_instance(instance, session)
        return BaseSuccessResponse(message=f"{self.model_name} was deleted")

    async def patch_instance(
        self, pk: int , instance_pydantic_model: BaseModel, session: AsyncSession
    ) -> T:
        instance = await self.get_instance_by_pk(pk, session)
        patched_instance = await self.update_instance(instance, instance_pydantic_model, session)
        return patched_instance

    async def get_page_data(self, page: int, session: AsyncSession) -> Tuple:
        all_instance = await self.get_all_instance(page, session)
        total_count = await self.get_total_count(session)
        return all_instance, total_count