from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.repositories.user import BaseUserRepository
from app.models import (
    Student, StudentCourse, User,
    StudentLesson, StudentLessonTask,
)
from app.schemas import LessonStudentAnswersResponse


class StudentRepository(BaseUserRepository[Student]):
    def __init__(self):
        super().__init__(Student)

    async def get_instance_by_pk(self, pk: int, session: AsyncSession) -> Student:
        statement = (
            select(self.model)
            .where(self.model_pk==pk)
            .options(selectinload(self.model.user))
        )
        result = await session.execute(statement)
        instance = result.scalar_one_or_none()
        return instance

    async def add_to_course(self, session: AsyncSession, **student_course) -> StudentCourse:
        new_instance = StudentCourse(**student_course)
        session.add(new_instance)
        await session.commit()
        return new_instance

    async def insert_new_results(
        self, student_id: int, student_answers: LessonStudentAnswersResponse, session: AsyncSession,
    ) -> None:
        student_lesson_instance = StudentLesson(
            student_id=student_id, lesson_id=student_answers.lesson_id,
            result=student_answers.result, done=student_answers.done
        )
        session.add(student_lesson_instance)
        await session.flush()
        for answer in student_answers.answers:
            student_lesson_task_instanse = StudentLessonTask(
                lesson_task_id=answer.lesson_task_id,
                student_lesson_id=student_lesson_instance.student_lesson_id,
                answer=answer.answer,
                correct=answer.correct
            )
            session.add(student_lesson_task_instanse)
        await session.commit()

    async def update_results(
        self, student_lesson_instance: StudentLesson, student_answers: LessonStudentAnswersResponse, session: AsyncSession,
    ) -> None:
        student_lesson_instance.result = student_answers.result
        student_lesson_instance.done = student_answers.done
        for answer in student_answers.answers:
            statement = (
                select(StudentLessonTask)
                .where(StudentLessonTask.lesson_task_id==answer.lesson_task_id)
                .where(StudentLessonTask.student_lesson_id==student_lesson_instance.student_lesson_id)
            )
            student_lesson_task_instanse = await session.execute(statement)
            student_lesson_task_instanse: StudentLessonTask = student_lesson_task_instanse.scalars().first()
            student_lesson_task_instanse.answer = answer.answer
            student_lesson_task_instanse.correct = answer.correct
        await session.commit()

    async def answer_on_lesson(
        self, user: User, student_answers: LessonStudentAnswersResponse, session: AsyncSession,
    ) -> None:
        lesson_id: int = student_answers.lesson_id
        student_id: int = user.student.student_id
        statement = (
            select(StudentLesson)
            .where(StudentLesson.lesson_id==lesson_id)
            .where(StudentLesson.student_id==student_id)
        )
        result = await session.execute(statement)
        student_lesson_instance = result.scalar_one_or_none()
        if not student_lesson_instance:
            await self.insert_new_results(student_id, student_answers, session)
        else:
            await self.update_results(student_lesson_instance, student_answers, session)