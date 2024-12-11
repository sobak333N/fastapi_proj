from typing import Tuple, Type, Union, List

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    InputCourseSchema, ShortResponseCourseSchema,
    FullResponseCourseSchema, CoursePagedResponseSchema, 
)
from app.core.db import get_db
from app.auth.dependencies import RoleChecker, get_current_user
from app.models.user import Roles2, User
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
    course = await course_service.create_instance(course_data, session)
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
    updated_course = await course_service.patch_instance(course_id, course_data, session)
    return updated_course


@course_router.delete("/delete/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor])),
):
    return await course_service.delete_instance(user.instructor.instructor_id, course_id, session)


# @course_router.get("/", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
# async def get_courses(
#     session: AsyncSession,
#     course_ids: Optional[List[int]] = Query(None),  # Список ID категорий для фильтрации
#     min_price: Optional[float] = Query(None),  # Минимальная цена
#     max_price: Optional[float] = Query(None),  # Максимальная цена
#     page: int = 1,  # Страница для пагинации
#     page_size: int = 10,  # Размер страницы
# ):
#     # Строим запрос с фильтрацией
#     query = select(Course)

#     # Фильтрация по категориям
#     if course_ids:
#         query = query.filter(Course.course_id.in_(course_ids))

#     # Фильтрация по цене
#     if min_price is not None:
#         query = query.filter(Course.price >= min_price)
#     if max_price is not None:
#         query = query.filter(Course.price <= max_price)

#     # Пагинация
#     query = query.offset((page - 1) * page_size).limit(page_size)

#     # Выполняем запрос
#     result = await session.execute(query)
#     courses = result.scalars().all()

#     if not courses:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found")

#     return courses
