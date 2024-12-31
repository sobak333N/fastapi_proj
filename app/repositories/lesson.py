from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.repositories.base_repository import DocumentRepository
from app.models import Lesson, LessonDocument, User
from app.schemas import LessonSchema


class LessonRepository(DocumentRepository[Lesson, LessonDocument]):
    def __init__(self):
        super().__init__(Lesson, LessonDocument)
        
    async def create_instance(
        self, 
        session: AsyncSession, 
        no_commit: bool=False, 
        **kwargs
    ) -> Optional[LessonSchema]:
        course = {}
        for attr, value in kwargs.items():
            if attr == "course_id":
                course = {attr: value}
        
        kwargs.pop("course_id")
        
        
        lesson_relation = await super().create_instance(session=session, **course)
        lesson_document = self.document_model(
            lesson_id=lesson_relation.lesson_id,
            materials=[],
            **kwargs
        )
        await lesson_document.insert()
        lesson_schema_dict = {
            **jsonable_encoder(lesson_document), 
            **jsonable_encoder(lesson_relation), 
        }
        return LessonSchema(**lesson_schema_dict)
    
    async def update_instance(
        self, instance: Lesson, session: AsyncSession, no_commit = False, **kwargs
    ) -> LessonSchema:
        course = {}
        for attr, value in kwargs.items():
            if attr == "course_id":
                course = {attr: value}
        
        kwargs.pop("course_id")
        lesson_relation = await super().update_instance(instance, session, **course)

        lesson_document = await self.document_model.find_one(
            self.document_model.lesson_id == instance.lesson_id
        ).set(**kwargs)
        lesson_schema_dict = {
            **jsonable_encoder(lesson_relation),
            **jsonable_encoder(lesson_document)
        }
        return LessonSchema(**lesson_schema_dict)