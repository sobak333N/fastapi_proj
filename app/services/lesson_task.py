from app.services.base_service import BaseService
from app.repositories import LessonTaskRepository


class LessonTaskService(BaseService):
    def __init__(self):
        super().__init__(LessonTaskRepository, "LessonTask")