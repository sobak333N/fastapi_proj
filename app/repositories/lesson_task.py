from app.models import LessonTask
from app.repositories.base_repository import BaseRepository


class LessonTaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(LessonTask)