from typing import Union, List
import copy

from pydantic import BaseModel, Field, model_validator

from app.schemas.other import (
    TextMaterial, ImageMaterial, VideoMaterial, 
    FormulaMaterial, TaskMaterial, SerializeMaterial,
    FullTaskMaterial
)


InputLessonSchema_model_config = {
    "json_schema_extra": {
        "examples": [
                {
                "course_id": 17,
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


class ShortLessonSchema(BaseModel):
    lesson_id: int = Field(..., description="lesson_id")
    lesson_name: str = Field(..., description="lesson_name")
    

class InputLessonSchema(BaseModel):
    course_id: int = Field(..., description="course_id")
    lesson_name: str = Field(..., description="lesson_name")
    
    model_config = InputLessonSchema_model_config



class UpdateLessonSchema(InputLessonSchema):
    materials: List[Union[
        TextMaterial, ImageMaterial, VideoMaterial,
        FormulaMaterial, TaskMaterial
    ]] = Field(
        default=[],
        description="materials"
    )
    
    @model_validator(mode="after")
    def materials_validator(cls, model):
        model.materials = [
            material if isinstance(material, TaskMaterial)
            else SerializeMaterial.process(material, SerializeMaterial.material_type_dict)
            for material in model.materials
        ]
        return model
    
    model_config = UpdateLessonSchema_model_config


class LessonSchema(UpdateLessonSchema):
    lesson_id: int = Field(..., description="lesson_id")
    
    model_config = LessonSchema_model_config


class GetLessonSchema(LessonSchema):
    materials: List[Union[
        TextMaterial, ImageMaterial, VideoMaterial,
        FormulaMaterial, FullTaskMaterial
    ]] = Field(
        default=[],
        description="materials"
    )
    
    @model_validator(mode="after")
    def materials_validator(cls, model):
        model.materials = [
            material if isinstance(material, TaskMaterial)
            else SerializeMaterial.process(material, SerializeMaterial.get_lesson_material_type_dict)
            for material in model.materials
        ]
        return model