from typing import List
from pydantic import BaseModel

from app.config import Config

class PagedResponseSchema(BaseModel):
    data: List[BaseModel]
    page: int
    count_on_page: int
    total_count: int