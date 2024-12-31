from typing import Optional, List
import copy

from pydantic import BaseModel, Field

from app.models.lesson_task import TaskTypeEnum

InputLessonTaskSchema_model_config = {
    "json_schema_extra": {
        "examples": [
            {
                "lesson_id": 1,
                "question": "integrate x^3 from -1 to 1",
                "task_type": "Test",
                "options": [0,10,228],
                "answer": 0
            },
            {
                "lesson_id": 1,
                "question": "integrate x^3 from -1 to 1",
                "task_type": "Assignment",
                "options": None,
                "answer": 0
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
    options: Optional[List[int]] = Field(default=None)
    answer: str = Field(..., description="answer")
    
    model_config = InputLessonTaskSchema_model_config


class LessonTaskSchema(InputLessonTaskSchema):
    lesson_task_id: int = Field(..., description="lesson_id")

    model_config = LessonTaskSchema_model_config
