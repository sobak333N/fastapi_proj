from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LessonTask, LessonTaskDocument, User
from app.repositories.base_repository import DocumentRepository
from app.schemas import LessonTaskSchema


class LessonTaskRepository(DocumentRepository[LessonTask, LessonTaskDocument]):
    def __init__(self):
        super().__init__(LessonTask, LessonTaskDocument)
    
    async def create_instance(
        self, 
        user: User,
        session: AsyncSession, 
        no_commit: bool=False, 
        **kwargs
    ) -> Optional[LessonTaskSchema]:

        lesson = {}        
        for attr, value in kwargs.items():
            if attr == "lesson_id":
                lesson = {attr: value}
                
        lesson_task = await super().create_instance(session, **lesson)
        lesson_task_document = self.document_model(**kwargs)
        lesson_task_schema_dict = {
            **lesson_task, **lesson_task_document
        }
        return LessonTaskSchema(**lesson_task_schema_dict)