from app.repositories.user import BaseRepository
from app.models import Instructor


class InstructorRepository(BaseRepository):
    def __init__(self):
        return super().__init__(Instructor)