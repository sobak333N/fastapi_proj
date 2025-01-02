from typing import Optional, List, Type

from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    LessonTask, LessonTaskDocument, 
    User, Lesson, LessonDocument,
)
from app.repositories.base_repository import DocumentRepository
from app.repositories.redis import RedisInstanced
from app.schemas.other import MaterialType, TaskMaterial
from app.schemas import LessonTaskSchema


class RedisLessonTask(RedisInstanced):
    
    key_suffix_type: Type=LessonTask
    
    @classmethod
    def find_key_suffix(cls, args, kwargs):
        for arg in args:
            if isinstance(arg, cls.key_suffix_type):
                return str(arg.lesson_id)


class RedisLessonTaskCreate(RedisInstanced):
    
    @classmethod
    def find_key_suffix(cls, args, kwargs):
        for attr, value in kwargs.items():
            if attr=="lesson_id":
                return str(value)


class LessonTaskRepository(DocumentRepository[LessonTask, LessonTaskDocument]):
    def __init__(self):
        super().__init__(LessonTask, LessonTaskDocument)
    
    @RedisLessonTaskCreate.del_cache("lesson_")
    async def create_instance(
        self, 
        session: AsyncSession, 
        no_commit: bool=False, 
        **kwargs
    ) -> Optional[LessonTaskSchema]:

        lesson = {}        
        for attr, value in kwargs.items():
            if attr == "lesson_id":
                lesson = {attr: value}
                
        lesson_task = await super().create_instance(session, no_commit, **lesson)
        lesson_task_document = self.document_model(
            lesson_task_id=lesson_task.lesson_task_id, **kwargs
        )
        await lesson_task_document.insert()
        lesson_document = await LessonDocument.find_one(
            LessonDocument.lesson_id==lesson_task.lesson_id
        )
        lesson_document.materials.append(
            TaskMaterial(lesson_task_id=lesson_task.lesson_task_id)
        )
        await lesson_document.save()
        lesson_task_schema_dict = {
            **jsonable_encoder(lesson_task), 
            **jsonable_encoder(lesson_task_document)
        }
        return LessonTaskSchema(**lesson_task_schema_dict)
    
    async def get_all_tasks_of_lesson(
        self, lesson: Lesson, session: AsyncSession,
    ) -> List[LessonTask]:
        stmt = (
            select(LessonTask)
            .where(LessonTask.lesson_id==lesson.lesson_id)
        )
        tasks = await session.execute(stmt)
        return tasks.scalars().all()

    async def get_all_task_documents_of_lesson(
        self, lesson: Lesson
    ) -> List[LessonTaskDocument]:
        return await LessonTaskDocument.find(
            LessonTaskDocument.lesson_id==lesson.lesson_id
        ).to_list()

    @RedisLessonTask.del_cache("lesson_")
    async def update_instance(
        self, instance: LessonTask, session: AsyncSession, no_commit: bool=False, **kwargs
    ) -> LessonTaskSchema:

        lesson = {}        
        for attr, value in kwargs.items():
            if attr == "lesson_id":
                lesson = {attr: value}
        lesson_task = await super().update_instance(instance, session, no_commit, **lesson)
        lesson_task_document = await self.document_model.find_one(
            self.document_model.lesson_task_id==lesson_task.lesson_task_id
        )
        for attr, value in kwargs.items():
            if attr in lesson_task_document.__dict__.keys():
                setattr(lesson_task_document, attr, value)
        
        await lesson_task_document.save()
        lesson_task_schema_dict = {
            **jsonable_encoder(lesson_task), 
            **jsonable_encoder(lesson_task_document)
        }
        return LessonTaskSchema(**lesson_task_schema_dict)

    @RedisLessonTask.del_cache("lesson_")
    async def delete_instance(
        self, instance: LessonTask, session: AsyncSession, no_commit: bool=False
    ) -> None:
        lesson_task_document = await self.document_model.find_one(
            self.document_model.lesson_task_id==instance.lesson_task_id
        )
        await lesson_task_document.delete()
        lesson_document = await LessonDocument.find_one(
            LessonDocument.lesson_id==instance.lesson_id
        )
        lesson_document.materials = [
            material for material in lesson_document.materials
            if not(material.type == MaterialType.lesson_task 
            and material.lesson_task_id == instance.lesson_task_id)
        ]
        await lesson_document.save()
        await super().delete_instance(instance, session, no_commit)