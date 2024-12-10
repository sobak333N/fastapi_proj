from typing import Type, TypeVar, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from sqlalchemy.future import select
from sqlalchemy import update


T = TypeVar('T')

class BaseRepository:
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

    async def get_instance_by_unique_field(self, unique_attr: str, value: Any, session: AsyncSession) -> Optional[T]:
        if hasattr(self.model, unique_attr):
            statement = (
                select(self.mode)
                .where(self.model.unique_attr == value)
            )
            result = await session.execute(statement)
            instance = result.scalar_one_or_none()
            return instance
        return None

    async def create_instance(self, session: AsyncSession, **kwargs) -> Optional[T]:
        new_instance = self.model(**kwargs)
        session.add(new_instance)
        await session.commit()
        return new_instance

    async def set_value(self, instance: T, attr: str, value: Any, session: AsyncSession) -> Optional[T]:
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
            await session.commit()
            updated_instance = result.scalar_one_or_none()
            return updated_instance
        return None
    
    async def update_instance(self, instance: T, session: AsyncSession, **kwargs) -> Optional[T]:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        session.add(instance)
        await session.commit()
        return instance
