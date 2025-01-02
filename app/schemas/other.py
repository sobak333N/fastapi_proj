from enum import Enum as PyEnum
from typing import Union, List, Dict, Type
import copy

from pydantic import BaseModel, Field
from pydantic_core import PydanticCustomError
from fastapi.encoders import jsonable_encoder

from app.schemas.lesson_task import LessonTaskSchema


class MaterialType(PyEnum):
    text = "text"
    image = "image"
    video = "video"
    formula = "formula"
    lesson_task = "task"


class BaseMaterial(BaseModel):
    type: MaterialType = Field(..., description="Тип материала") 


class TextMaterial(BaseMaterial):
    type: MaterialType = MaterialType.text
    data: str = Field(..., description="Текст материала")


class ImageMaterial(BaseMaterial):
    type: MaterialType = MaterialType.image
    data: str = Field(..., description="Ссылка на изображение")


class VideoMaterial(BaseMaterial):
    type: MaterialType = MaterialType.video
    data: str = Field(..., description="Ссылка на видео")


class FormulaMaterial(BaseMaterial):
    type: MaterialType = MaterialType.formula
    data: str = Field(..., description="Формула в LaTeX формате")


class TaskMaterial(BaseMaterial):
    type: MaterialType = MaterialType.lesson_task
    lesson_task_id: int = Field(..., description="ID задачи из MongoDB")


class FullTaskMaterial(BaseMaterial):
    type: MaterialType = MaterialType.lesson_task
    lesson_task: LessonTaskSchema


class PagedResponseSchema(BaseModel):
    data: List[BaseModel]
    page: int
    count_on_page: int
    total_count: int
    
class S3LinkResponse(BaseModel):
    message: str=Field(default="File was successfully uploaded")
    link: str=Field(..., description="link in s3 storage")

class SerializeMaterial:
    material_type_dict: Dict[MaterialType, Type[BaseMaterial]] = {
        MaterialType.text: TextMaterial,
        MaterialType.image: ImageMaterial,
        MaterialType.video: VideoMaterial,
        MaterialType.formula: FormulaMaterial,
        MaterialType.lesson_task: TaskMaterial,
    }

    get_lesson_material_type_dict: Dict[MaterialType, Type[BaseMaterial]] = copy.deepcopy(material_type_dict)
    get_lesson_material_type_dict[MaterialType.lesson_task] = FullTaskMaterial


    @staticmethod
    def process(
        material: BaseMaterial, material_types_dict: Dict[MaterialType, Type[BaseMaterial]]
    ) -> BaseMaterial:
        material_type = getattr(material, "type")
        material_class = material_types_dict.get(material_type)
        if not material_class:
            raise PydanticCustomError(
                f"value_error.type",
                f"type cannot be not enum", 
                {"input": getattr(material, "type"), "expected": "Enum('text', 'image', 'video', 'formula', 'task')"}
                )
        return material_class(**jsonable_encoder(material))
