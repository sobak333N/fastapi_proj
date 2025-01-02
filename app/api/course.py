from typing import (
    Tuple, Type, Union, 
    List, Optional, Dict
)
from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    InputCourseSchema, ShortResponseCourseSchema,
    FullResponseCourseSchema, CoursePagedResponseSchema, 
    PrivateResponseCourseSchema,
)
from app.core.db import get_db
from app.auth.dependencies import (
    RoleChecker, get_current_user,
    not_required_get_current_user,
)
from app.models.user import Roles2, User
from app.models import Course
from app.services import CourseService


course_router = APIRouter()
course_service = CourseService()


@course_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=FullResponseCourseSchema)
async def create_course(
    course_data: InputCourseSchema,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    course_data.instructor_id = user.instructor.instructor_id
    course: Course = await course_service.create_instance(course_data, session)
    return course


@course_router.patch("/update/{course_id}", status_code=status.HTTP_200_OK, response_model=FullResponseCourseSchema)
async def patch_course(
    course_id: int,
    course_data: InputCourseSchema,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    course_data.instructor_id = user.instructor.instructor_id
    updated_course: Course = await course_service.patch_instance(course_id, user, course_data, session)
    return updated_course


@course_router.delete("/delete/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await course_service.delete_instance(user, course_id, session)


@course_router.post("/", status_code=status.HTTP_200_OK, response_model=CoursePagedResponseSchema)
async def get_courses(
    category_ids: Optional[List[int]], 
    start_cost: Optional[int]=0,
    end_cost: Optional[int]=1_000_000,
    session: AsyncSession=Depends(get_db),
    page: int = 1,
):
    total_count: int = await course_service.get_total_count(session)
    courses: Course = await course_service.get_all_instance(page, category_ids, start_cost, end_cost, session)
    data: List[Dict] = [jsonable_encoder(course) for course in courses]

    page_data: CoursePagedResponseSchema = CoursePagedResponseSchema(
        data=data,
        page=page,
        count_on_page=len(data),
        total_count=total_count
    )

    return page_data


@course_router.get(
    "/get/{course_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=PrivateResponseCourseSchema
)
async def get_course_by_id(
    course_id: int,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(not_required_get_current_user)
):
    course: Course = await course_service.get_instance_by_pk(course_id, user, session)
    return course