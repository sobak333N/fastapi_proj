from typing import Tuple, Any
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.repositories import CategoryRepository, RedisPaged


class CategoryService(BaseService):
    def __init__(self):
        super().__init__(CategoryRepository, "Category")

    @RedisPaged.get_cache("category_page_")
    async def get_page_data(self, page: int, session: AsyncSession) -> Tuple:
        return await super().get_page_data(page, session)
    
    @RedisPaged.del_cache("category_page_")
    async def create_instance(self, instance_pydatinc_model: BaseModel, session: AsyncSession):
        return await super().create_instance(instance_pydatinc_model, session)

    @RedisPaged.del_cache("category_page_")
    async def update_instance(self, instance: Any, instance_pydatinc_model: BaseModel, session: AsyncSession):
        return await super().update_instance(instance, instance_pydatinc_model, session)

    @RedisPaged.del_cache("category_page_")
    async def delete_instance(self, pk: int, session: AsyncSession) -> None:
        return await super().delete_instance(pk, session)