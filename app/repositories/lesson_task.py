from app.models import LessonTask, LessonTaskDocument
from app.repositories.base_repository import DocumentRepository


class LessonTaskRepository(DocumentRepository[LessonTask, LessonTaskDocument]):
    def __init__(self):
        super().__init__(LessonTask, LessonTaskDocument)