from typing import (
    Type, TypeVar, Any, 
    Optional, List, Generic,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from sqlalchemy.future import select
from sqlalchemy import update, func, inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.collections import InstrumentedList

from app.core.db import get_db, Base
from app.config import Config


T = TypeVar('T')
D = TypeVar('D')


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        mapper = class_mapper(self.model)
        primary_key = mapper.primary_key
        self.primary_key = primary_key[0].name
        self.model_pk = getattr(self.model, self.primary_key)

    async def get_instance_by_pk(self, pk: int, session: AsyncSession) -> Optional[T]:
        statement = (
            select(self.model)
            .where(self.model_pk==pk)
        )
        result = await session.execute(statement)
        instance = result.scalar_one_or_none()
        return instance

    # async def get_instance_by_unique_field(
    #         self, 
    #         unique_attr: str, 
    #         value: Any, 
    #         session: AsyncSession
    #     ) -> Optional[T]:
    #     if hasattr(self.model, unique_attr):
    #         statement = (
    #             select(self.mode)
    #             .where(self.model.unique_attr == value)
    #         )
    #         result = await session.execute(statement)
    #         instance = result.scalar_one_or_none()
    #         return instance
    #     return None

    async def get_all_instance(self, page: int , session: AsyncSession) -> List[T]:
        statement = (
            select(self.model)
            .order_by(self.model_pk)
            .offset(Config.PAGE_LIMIT*(page-1))
            .limit(Config.PAGE_LIMIT)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_total_count(self, session: AsyncSession) -> List[T]:
        statement = select(func.count()).select_from(self.model)
        result = await session.execute(statement)
        return result.scalar()

    async def create_instance(self, session: AsyncSession, no_commit: bool=False, **kwargs) -> Optional[T]:
        new_instance = self.model(**kwargs)
        session.add(new_instance)
        if not no_commit:
            await session.commit()
        return new_instance

    async def set_value(
        self, 
        instance: T, 
        attr: str, 
        value: Any, 
        session: AsyncSession, 
        no_commit: bool=False
    ) -> Optional[T]:
        if hasattr(instance, attr):
            instance_pk = getattr(instance, self.primary_key)
            statement = (
                update(self.model)
                .where(self.model_pk == instance_pk)
                .values({attr: value})
                .execution_options(synchronize_session="fetch")
                .returning(self.model)
            )
            result = await session.execute(statement)
            if not no_commit:
                await session.commit()
            updated_instance = result.scalar_one_or_none()
            return updated_instance
        return None
    
    async def update_instance(self, instance: T, session: AsyncSession, no_commit: bool=False, **kwargs) -> Optional[T]:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        if not no_commit:
            await session.commit()
        return instance


    async def raw_update_instance(self, instance: T, session: AsyncSession, no_commit: bool=False, **kwargs) -> Optional[T]:
        values = {
            key: value
            for key, value in instance.__dict__.items()
            if not key.startswith('_') and 
            not isinstance(value, (InstrumentedList, InstrumentedAttribute, Base))
        }
        instance_pk = getattr(instance, self.primary_key)
        stmt = (
            update(self.model)
            .where(self.model_pk == instance_pk)
            .values(**(values))
            .execution_options(synchronize_session="fetch")
            .returning(self.model)
        )
        result = await session.execute(stmt)
        if not no_commit:
            await session.commit()
        updated_instance = result.scalar_one_or_none()
        return updated_instance


    async def delete_instance(self, instance: T , session: AsyncSession, no_commit: bool=False) -> None:
        await session.delete(instance)
        if not no_commit:
            await session.commit()


class DocumentRepository(Generic[T, D], BaseRepository[T]):
    def __init__(self, model: Type[T], document_model: Type[D]):
        super().__init__(model)
        self.document_model = document_model