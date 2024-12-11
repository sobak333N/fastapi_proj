from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.other import PagedResponseSchema


class BaseCategorySchema(BaseModel):
    category_name: str


class CategorySchema(BaseCategorySchema):
    category_description: Optional[str]=None
    keywords: Optional[str]=None

class ResponseCategorySchema(BaseCategorySchema):
    category_id: int

class CategoryPagedResponseSchema(PagedResponseSchema):
    data: List[ResponseCategorySchema]