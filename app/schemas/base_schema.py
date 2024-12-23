# from pydantic import BaseModel, ValidationError
# from typing import List, Dict, Any


# class BaseValidationModel(BaseModel):
    
#     @classmethod
#     def validate(cls, **data: Any):
#         try:
#             return super().validate(**data)
#         except ValidationError as e:
#             formatted_errors = []
#             for error in e.errors():
#                 formatted_errors.append({
#                     "loc": error["loc"],

                    
#                 })
#             raise ValidationError(formatted_errors, cls)