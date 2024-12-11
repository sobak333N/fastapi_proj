from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.other import PagedResponseSchema


class BaseCategorySchema(BaseModel):
    category_name: str


class InputCategorySchema(BaseCategorySchema):
    category_description: Optional[str]=None
    keywords: Optional[str]=None


class ShortResponseCategorySchema(BaseCategorySchema):
    category_id: int


class FullResponseCategorySchema(InputCategorySchema, ShortResponseCategorySchema):
    pass


class CategoryPagedResponseSchema(PagedResponseSchema):
    data: List[ShortResponseCategorySchema]