from .base_repository import BaseRepository
from app.models import Category


class CategoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Category)
    