from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from app.schemas.other import PagedResponseSchema
from app.models.course import Difficulty

course_config = {
    "json_schema_extra": {
        "example": {
            "category_id": 2,
            "course_name": "math and geom",
            "cost": 2000,
            "difficulty": "easy",
        }
    }
}

class BaseCourseSchema(BaseModel):
    category_id: int
    course_name: str = Field(min_length=1, max_length=128)
    cost: int = Field(gt=0)
    difficulty: Difficulty


class InputCourseSchema(BaseCourseSchema):
    instructor_id: Optional[int]=None
    model_config = course_config

class ShortResponseCourseSchema(BaseCourseSchema):
    course_id: int
    instructor_id: int


class FullResponseCourseSchema(ShortResponseCourseSchema, InputCourseSchema):
    pass

class PrivateResponseCourseSchema(FullResponseCourseSchema):
    private_info: Optional[str] = None

    @field_validator("private_info", mode="after")
    def validate_private_info(cls, value: str, info):
        if value is not None and not value.strip():
            raise PydanticCustomError(
                f"value_error.non_empty",
                f"{info.field_name} cannot be empty or only whitespace", 
                {"input": value, "expected": "non empty"}
            )
        return value


class CoursePagedResponseSchema(PagedResponseSchema):
    data: List[ShortResponseCourseSchema]