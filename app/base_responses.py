from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.schemas import PagedResponseSchema


class BaseSuccessResponse(JSONResponse):
    def __init__(self, message: str=None):
        content={
            "success": "success",
            "message": message    
        }
        super().__init__(content=content)

    
class PagedResponse(JSONResponse):
    def __init__(self, page_data: PagedResponseSchema):
        content = jsonable_encoder(page_data)
        super().__init__(content=content)