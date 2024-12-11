from typing import Optional, List
from pydantic import BaseModel, Field

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
    course_name: str
    cost: int
    difficulty: Difficulty


class InputCourseSchema(BaseCourseSchema):
    instructor_id: Optional[int]=None
    model_config = course_config

class ShortResponseCourseSchema(BaseCourseSchema):
    course_id: int
    instructor_id: int


class FullResponseCourseSchema(ShortResponseCourseSchema, InputCourseSchema):
    pass


class CoursePagedResponseSchema(PagedResponseSchema):
    data: List[ShortResponseCourseSchema]