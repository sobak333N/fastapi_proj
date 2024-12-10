from datetime import datetime, timedelta
import json
from typing import Tuple, Type, Union

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CategorySchema
from app.core.db import get_db
from app.auth.dependencies import RoleChecker
from app.models.user import Roles2
from app.services import CategoryService

category_router = APIRouter()
category_service = CategoryService()


@category_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategorySchema,
    session: AsyncSession=Depends(get_db),
    permission: bool=Depends(RoleChecker([Roles2.admin])),
):
    category_dict = jsonable_encoder(category_data)
    category = await category_service.create_instance(session, **category_dict)
    return category


@category_router.patch("/update/{category_id}", status_code=status.HTTP_200_OK)
async def create_category(
    category_id: int,
    category_data: CategorySchema,
    session: AsyncSession=Depends(get_db),
    permission: bool=Depends(RoleChecker([Roles2.admin])),
):
    category_dict = jsonable_encoder(category_data)
    category = await category_service.get_instance_by_pk(category_id, session)
    print("XXXXXX")
    updated_category = await category_service.update_instance(category, session, **category_dict)
    return updated_category