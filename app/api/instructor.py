from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    ShortInstructorResponse, InstructorResponse,
    UpdateInstructorResponse,
)
from app.core.db import get_db
from app.services import InstructorService
from app.models import User
from app.models.user import Roles2
from app.auth.dependencies import get_current_user, RoleChecker




instructor_router = APIRouter()
instructor_service = InstructorService()


@instructor_router.get("/get/{instructor_id}", status_code=status.HTTP_200_OK, response_model=ShortInstructorResponse)
async def get_course_by_id(
    instructor_id: int,
    session: AsyncSession=Depends(get_db),
):
    instructor = await instructor_service.get_instance_by_pk(instructor_id, session)
    reponse = ShortInstructorResponse(**jsonable_encoder(instructor)).model_dump()
    return reponse


@instructor_router.patch("/patch", status_code=status.HTTP_200_OK, response_model=InstructorResponse)
async def patch_instructor(
    instructor_model: UpdateInstructorResponse,
    session: AsyncSession=Depends(get_db),
    user: User=Depends(get_current_user),
    permission: bool=Depends(RoleChecker([Roles2.instructor]))
):
    instructor = await instructor_service.patch_instance(instructor_model, user, session)
    return instructor
    # instructor = await instructor_service.get_instance_by_pk(instructor_id, session)
    # reponse = ShortInstructorResponse(**jsonable_encoder(instructor)).model_dump()
    # return reponse