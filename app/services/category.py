from app.services.base_service import BaseService
from app.repositories import CategoryRepository


class CategoryService(BaseService):
    def __init__(self):
        super().__init__(CategoryRepository, "Category")