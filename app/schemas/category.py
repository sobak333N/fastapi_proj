from typing import Optional, List
from pydantic_core import PydanticCustomError
from pydantic import (
    field_validator, Field,
    BaseModel, 
)

from app.schemas.other import PagedResponseSchema


class BaseCategorySchema(BaseModel):
    category_name: str = Field(min_length=1, max_length=128)


class InputCategorySchema(BaseCategorySchema):
    category_description: Optional[str]=None
    keywords: Optional[str]=None

    @field_validator("category_description", "keywords", mode="after")
    def non_empty_validator(cls, value: str, info):
        if value is not None and not value.strip():
            raise PydanticCustomError(
                f"value_error.non_empty",
                f"{info.field_name} cannot be empty or only whitespace", 
                {"input": value, "expected": "non empty"}
            )
        return value

class ShortResponseCategorySchema(BaseCategorySchema):
    category_id: int


class FullResponseCategorySchema(InputCategorySchema, ShortResponseCategorySchema):
    pass


class CategoryPagedResponseSchema(PagedResponseSchema):
    data: List[ShortResponseCategorySchema]