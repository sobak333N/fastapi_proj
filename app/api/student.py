from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    ShortStudentResponse, UpdateStudentResponse,
    StudentResponse, LessonStudentAnswers,
)
from app.core.db import get_db
from app.services import StudentService
from app.models import User
from app.models.user import Roles2
from app.models.course import PaymentType
from app.auth.dependencies import get_current_user, RoleChecker


student_router = APIRouter()
student_service = StudentService()


@student_router.get("/get/{student_id}", status_code=status.HTTP_200_OK, response_model=ShortStudentResponse)
async def get_student_by_id(
    student_id: int,
    session: AsyncSession=Depends(get_db),
):
    student = await student_service.get_instance_by_pk(student_id, session)
    reponse = ShortStudentResponse(**jsonable_encoder(student)).model_dump()
    return reponse


@student_router.patch("/patch", status_code=status.HTTP_200_OK, response_model=StudentResponse)
async def patch_instructor(
    student_model: UpdateStudentResponse,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.student]))
):
    return await student_service.patch_instance(student_model, user, session)


@student_router.post("/buy-course/{course_id}", status_code=status.HTTP_200_OK)
async def buy_course(
    course_id: int,
    payment_type: PaymentType,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),   
    permission: bool=Depends(RoleChecker([Roles2.student])),
):
    return await student_service.buy_course(
        course_id=course_id, 
        user=user,
        student_id=user.student.student_id, 
        payment_type=payment_type,
        session=session
    )


@student_router.post("/answer/{lesson_id}", status_code=status.HTTP_200_OK)
async def answer_on_lesson(
    lesson_id: int,
    student_answers: LessonStudentAnswers,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.student]))
):
    return await student_service.answer_on_lesson(
        lesson_id, user, student_answers, session
    )