from typing import Tuple, Type, Union, List

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    InputCategorySchema, 
    ShortResponseCategorySchema,
    CategoryPagedResponseSchema, FullResponseCategorySchema
)
from app.core.db import get_db
from app.auth.dependencies import RoleChecker
from app.models.user import Roles2
from app.services import CategoryService


category_router = APIRouter()
category_service = CategoryService()


@category_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=FullResponseCategorySchema)
async def create_category(
    category_data: InputCategorySchema,
    session: AsyncSession=Depends(get_db),
    permission: bool=Depends(RoleChecker([Roles2.admin])),
):
    category = await category_service.create_instance(category_data, session)
    return category


@category_router.patch("/update/{category_id}", status_code=status.HTTP_200_OK, response_model=FullResponseCategorySchema)
async def patch_category(
    category_id: int,
    category_data: InputCategorySchema,
    session: AsyncSession=Depends(get_db),
    permission: bool=Depends(RoleChecker([Roles2.admin])),
):
    updated_category = await category_service.patch_instance(category_id, category_data, session)
    return updated_category


@category_router.delete("/delete/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    session: AsyncSession=Depends(get_db),
    permission: bool=Depends(RoleChecker([Roles2.admin])),
):
    return await category_service.delete_instance(category_id, session)


@category_router.get("/get/{category_id}", status_code=status.HTTP_200_OK, response_model=FullResponseCategorySchema)
async def get_category(
    category_id: int,
    session: AsyncSession=Depends(get_db),
):
    category = await category_service.get_instance_by_pk(category_id, session)
    return category


@category_router.get("/get", status_code=status.HTTP_200_OK, response_model=CategoryPagedResponseSchema)
async def get_all_category(
    session: AsyncSession=Depends(get_db),
    page: int=1,
):
    categories, total_count = await category_service.get_page_data(page, session)
    data = [
        jsonable_encoder(ShortResponseCategorySchema(
            category_name=category["category_name"], 
            category_id=category["category_id"]
        ))
        for category in categories
    ]
    page_data = CategoryPagedResponseSchema(
        data=data,
        page=page,
        count_on_page=len(data),
        total_count=total_count
    )

    return page_data