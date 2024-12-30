from typing import List
from pydantic import BaseModel, Field

from app.config import Config

class PagedResponseSchema(BaseModel):
    data: List[BaseModel]
    page: int
    count_on_page: int
    total_count: int
    
class S3LinkResponse(BaseModel):
    message: str=Field(default="File was successfully uploaded")
    link: str=Field(..., description="link in s3 storage")