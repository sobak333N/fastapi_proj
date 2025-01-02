from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.encoders import jsonable_encoder

from app.repositories.base_repository import DocumentRepository
from app.models import Lesson, LessonDocument, User, LessonTaskDocument
from app.models.lesson import TaskMaterial
from app.schemas import (
    LessonSchema, GetLessonSchema, 
    FullTaskMaterial, LessonTaskSchema,
)


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
        lesson_relation = await super().create_instance(session=session, no_commit=no_commit, **course)
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
        self, instance: Lesson, session: AsyncSession, no_commit: bool=False, **kwargs
    ) -> LessonSchema:
        course = {}
        for attr, value in kwargs.items():
            if attr == "course_id":
                course = {attr: value}
        
        kwargs.pop("course_id")
        lesson_relation = await super().update_instance(instance, session, no_commit, **course)

        lesson_document = await self.document_model.find_one(
            self.document_model.lesson_id == instance.lesson_id
        )
        for attr, value in kwargs.items():
            if attr in lesson_document.__dict__.keys(): 
                setattr(lesson_document, attr, value)
        await lesson_document.save()
        lesson_schema_dict = {
            **jsonable_encoder(lesson_relation),
            **jsonable_encoder(lesson_document)
        }
        return LessonSchema(**lesson_schema_dict)
    
    async def delete_instance(
        self, instance: Lesson, session: AsyncSession, no_commit: bool=False
    ) -> None:
        lesson_document = await self.document_model.find_one(
            self.document_model.lesson_id == instance.lesson_id
        )
        await lesson_document.delete()
        await LessonTaskDocument.find(
            LessonTaskDocument.lesson_id==instance.lesson_id 
        ).delete_many()
        await super().delete_instance(instance, session, no_commit)
        
    async def get_document_by_pk(self, pk: int, lesson: Lesson, session: AsyncSession) -> GetLessonSchema:
        lesson_document = await self.document_model.find_one(
            self.document_model.lesson_id==pk
        )
        lesson_task_documents = await LessonTaskDocument.find(
            LessonTaskDocument.lesson_id==pk
        ).to_list()
        
        def find_in_lesson_task_documents(lesson_task_id: int) -> FullTaskMaterial:
            for lesson_task in lesson_task_documents:
                if lesson_task.lesson_task_id == lesson_task_id:
                    jsonable_encoded_data = jsonable_encoder(lesson_task)
                    return FullTaskMaterial(
                        lesson_task=LessonTaskSchema(**jsonable_encoded_data)
                    )
 
        lesson_document.materials = [
            material if not isinstance(material, TaskMaterial) 
            else find_in_lesson_task_documents(material.lesson_task_id) 
            for material in lesson_document.materials
        ]
        return GetLessonSchema(
            course_id=lesson.course_id,
            **jsonable_encoder(lesson_document)
        )