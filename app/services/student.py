from typing import Any, List
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.repositories import StudentRepository, CourseRepository
from app.repositories.user import RedisUser, UserRepository
from app.models.course import PaymentType, PaymentStatus
from app.models import Course, User, Student, LessonTaskDocument
from app.schemas import (
    UpdateStudentResponse, LessonStudentAnswers,
    LessonStudentAnswersResponse, LessonStudentAnswerResponse
)
from app.base_responses import BaseSuccessResponse
from app.services.course import CourseService
from app.services.lesson import LessonService
from app.errors import NotCorrectLessonTasks, InsufficientPermission
from app.task_manager import TaskManager
from app.config import Config
from app.core.db import get_session



class StudentService(BaseService[Student]):
    def __init__(self):
        super().__init__(StudentRepository, "Student")
        self.course_service = CourseService()
        self.user_repository = UserRepository()
        self.lesson_service = LessonService()

    async def get_instance_by_pk(self, pk: int, session: AsyncSession):
        student = await super().get_instance_by_pk(pk, session)
        for attr, value in student.user.__dict__.items():
            if not attr.startswith('_'):
                setattr(student, attr, value)
        delattr(student, 'user')
        return student
    
    async def buy_course(
        self, 
        course_id: int, 
        user: User,
        student_id: int, 
        payment_type: PaymentType,
        session: AsyncSession,
    ) -> BaseSuccessResponse:

        # checking existing of course
        await self.course_service.instance_exists(
            pk=course_id, 
            session=session
        )
        
        # background task with sending request to external financial service
        # asyncio.create_task()

        data = {
            "course_id": course_id,
            "student_id": student_id,
            "payment_type": payment_type,
            "payment_status": PaymentStatus.in_progress
        }
        await self.repository.add_to_course(session, **data)
        return BaseSuccessResponse("Waiting for processing for your payment")

    async def answer_on_lesson(
        self, lesson_id: int, user: User, student_answers: LessonStudentAnswers, session: AsyncSession 
    ) -> LessonStudentAnswersResponse:
        lesson = await self.lesson_service.get_instance_by_pk(lesson_id, session)
        student_access = await self.course_service.repository.check_access_of_user(
            course_id=lesson.course_id, 
            student_id=user.student.student_id, 
            session=session,
        )
        if not student_access: 
            raise InsufficientPermission()

        tasks = await self.lesson_service.lesson_task_repository.get_all_tasks_of_lesson(
            lesson, session
        )
        tasks = sorted([
            task.lesson_task_id for task in tasks
        ])
        input_tasks = sorted([
            student_answer.lesson_task_id for student_answer in student_answers.answers
        ])
        if input_tasks != tasks:
            raise NotCorrectLessonTasks()
        task_documents = await self.lesson_service.lesson_task_repository.get_all_task_documents_of_lesson(lesson)
        task_documents: List[LessonTaskDocument] = sorted(
            task_documents, key=lambda x: x.lesson_task_id
        )
        student_answers.answers = sorted(
            student_answers.answers, key=lambda x: x.lesson_task_id
        )
        response_answers: List[LessonStudentAnswerResponse] = []
        correct_amount: int = 0
        for student_answer, task_document in zip(student_answers.answers, task_documents):
            correct = bool(student_answer.answer == task_document.answer)
            correct_amount += 1 if correct else 0
            response_answers.append(
                LessonStudentAnswerResponse(
                    lesson_task_id=task_document.lesson_task_id,
                    answer=student_answer.answer,
                    correct=correct
                )
            )
        result = int((correct_amount/len(response_answers))*100)
        response = LessonStudentAnswersResponse(
            answers=response_answers, lesson_id=lesson.lesson_id,
            result=result, 
            done=bool(result >= Config.MIN_TEST_RESULT_TO_PASS)
        )
        async with get_session() as task_session:
            await TaskManager.create_task(
                self.repository.answer_on_lesson(user, response, task_session)
            )
        return response
                
        
    @RedisUser.del_cache(key_prefix="current_user")
    async def patch_instance(
        self, 
        student_model: UpdateStudentResponse, 
        user: User, 
        session: AsyncSession
    ) -> Any:
        excluded_fields = set([
            field for field, value in UpdateStudentResponse.model_config["fields"].items()
            if value.get("exclude", False) is True 
        ])
        for attr, value in student_model.__dict__.items():
            if attr not in excluded_fields:
                if attr in User.__dict__.keys():
                    setattr(user, attr, value)
                if attr in Student.__dict__.keys():
                    setattr(user.student, attr, value)

        updated_user = await self.user_repository.raw_update_instance(user, session, no_commit=True)
        updated_student = await self.repository.raw_update_instance(user.student, session, no_commit=True)
        await session.commit()
        updated_user.student = updated_student 

        for attr, value in updated_user.student.__dict__.items():
            if not attr.startswith('_'):
                setattr(updated_user, attr, value)
        return updated_user