# # app/api/course.py
# from fastapi import APIRouter, Query, HTTPException, status
# from app.models import Course
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import joinedload
# from app.schemas import CourseResponse  # Схема для курса
# from typing import List, Optional

# course_router = APIRouter()

# @course_router.get("/", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
# async def get_courses(
#     session: AsyncSession,
#     category_ids: Optional[List[int]] = Query(None),  # Список ID категорий для фильтрации
#     min_price: Optional[float] = Query(None),  # Минимальная цена
#     max_price: Optional[float] = Query(None),  # Максимальная цена
#     page: int = 1,  # Страница для пагинации
#     page_size: int = 10,  # Размер страницы
# ):
#     # Строим запрос с фильтрацией
#     query = select(Course)

#     # Фильтрация по категориям
#     if category_ids:
#         query = query.filter(Course.category_id.in_(category_ids))

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
