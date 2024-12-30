from app.models import Lesson
from app.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository):
    def __init__(self):
        super().__init__(Lesson)