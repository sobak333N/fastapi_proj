from typing import Union, List
import copy

from pydantic import BaseModel, Field

from app.models.lesson import (
    MaterialType, TextMaterial, 
    ImageMaterial, VideoMaterial, 
    FormulaMaterial, TaskMaterial,
)

InputLessonSchema_model_config = {
    "json_schema_extra": {
        "examples": [
                {
                "course_id": 1,
                "lesson_name": "lesson_name",
            }
        ]
    },
}

LessonSchema_model_config = copy.deepcopy(InputLessonSchema_model_config)
LessonSchema_model_config["json_schema_extra"]["examples"][0]["lesson_id"] = 1
LessonSchema_model_config["json_schema_extra"]["examples"][0]["materials"] = []



UpdateLessonSchema_model_config = copy.deepcopy(LessonSchema_model_config)
UpdateLessonSchema_model_config["json_schema_extra"]["examples"][0]["materials"] = [
    {"type": "text", "data": "some_text"},
    {"type": "image", "data": "link_for_image_in_s3"},
    {"type": "video", "data": "link_for_video_in_s3"},
    {"type": "formula", "data": "formula_in_LATEX_format"},
    {"type": "task", "lesson_task_id": 32},
]
UpdateLessonSchema_model_config["json_schema_extra"]["examples"][0].pop('lesson_id')

class InputLessonSchema(BaseModel):
    course_id: int = Field(..., description="course_id")
    lesson_name: str = Field(..., description="lesson_name")
    
    model_config = InputLessonSchema_model_config


class LessonSchema(InputLessonSchema):
    lesson_id: int = Field(..., description="lesson_id")
    materials: List[Union[
        TextMaterial, ImageMaterial, VideoMaterial,
        FormulaMaterial, TaskMaterial
    ]] = Field(
        default=[],
        description="materials"
    )
    
    model_config = LessonSchema_model_config


class UpdateLessonSchema(LessonSchema):
    materials: List[Union[
        TextMaterial, ImageMaterial, VideoMaterial,
        FormulaMaterial, TaskMaterial
    ]] = Field(
        default=[],
        description="materials"
    )
    lesson_id: int = Field(default=None, exclude=True)
    model_config = UpdateLessonSchema_model_config
    