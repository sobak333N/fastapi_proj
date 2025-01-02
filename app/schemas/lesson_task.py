from typing import Optional, List
import copy

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError

from app.models.lesson_task import TaskTypeEnum

InputLessonTaskSchema_model_config = {
    "json_schema_extra": {
        "examples": [
            {
                "lesson_id": 1,
                "question": "integrate x^3 from -1 to 1",
                "task_type": "Test",
                "options": ['0','10','228'],
                "answer": '0'
            },
            {
                "lesson_id": 1,
                "question": "integrate x^3 from -1 to 1",
                "task_type": "Assignment",
                "options": None,
                "answer": '0'
            }
        ]
    },
}

LessonTaskSchema_model_config = copy.deepcopy(InputLessonTaskSchema_model_config)
LessonTaskSchema_model_config["json_schema_extra"]["examples"][0]["lesson_task_id"] = 1


class InputLessonTaskSchema(BaseModel):
    lesson_id: int = Field(..., description="lesson_id")
    question: str = Field(..., description="question")
    task_type: TaskTypeEnum = Field(..., description="task_type")
    options: Optional[List[str]] = Field(default=None)
    answer: str = Field(..., description="answer")
    
    model_config = InputLessonTaskSchema_model_config
    
    @model_validator(mode="after")
    def validate_options_depends_on_task_type(cls, model):
        task_type = model.task_type
        options = model.options
        answer = model.answer
        
        if task_type == TaskTypeEnum.assignment and options is not None:
            raise PydanticCustomError(
                "value_error.options",
                "options must be none", 
                {"input": options, "expected": f"must be none with {TaskTypeEnum.assignment}"}
            )
        if task_type == TaskTypeEnum.test:
            if options is None:
                raise PydanticCustomError(
                    "value_error.options",
                    "options can't be none", 
                    {"input": options, "expected": f"can't be none with {TaskTypeEnum.test}"}
                )
            if answer not in options:
                raise PydanticCustomError(
                    "value_error.answer",
                    "answer must be in options", 
                    {"input": answer, "expected": f"answer include from {options}"}
                )
        return model        


class LessonTaskSchema(InputLessonTaskSchema):
    lesson_task_id: int = Field(..., description="lesson_id")

    model_config = LessonTaskSchema_model_config

class StudentLessonTaskSchema(LessonTaskSchema):
    answer: Optional[str] = Field(exclude=True, default=None)
    
    @model_validator(mode="after")
    def validate_options_depends_on_task_type(cls, model):
        return model
    
class UpdateLessonTaskSchema(InputLessonTaskSchema):
    pass