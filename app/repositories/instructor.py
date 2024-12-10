from app.repositories.user import BaseUserRepository
from app.models import Instructor


class InstructorRepository(BaseUserRepository):
    def __init__(self):
        return super().__init__(Instructor)