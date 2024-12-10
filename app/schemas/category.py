from typing import Optional
from pydantic import BaseModel, Field


class CategorySchema(BaseModel):
    category_name: str
    category_description: Optional[str]=None
    keywords: Optional[str]=None
