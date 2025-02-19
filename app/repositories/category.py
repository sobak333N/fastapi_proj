from typing import List, Optional, Any

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from app.models import Category
from app.config import Config
from app.repositories.redis import RedisPaged


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    async def get_all_instance(self, page: int, session: AsyncSession) -> List[Category]:
        statement = (
            select(Category.category_id, Category.category_name)
            .order_by(Category.category_id)
            .offset(Config.PAGE_LIMIT*(page-1))
            .limit(Config.PAGE_LIMIT)
        )
        result = await session.execute(statement)
        # return result.all()
        return [
            {"category_id": category[0], "category_name": category[1]}
            for category in result.fetchall()
        ]