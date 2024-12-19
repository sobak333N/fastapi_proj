from .user import UserResponse
from .instructor import InstructorResponse, ShortInstructorResponse
from .student import StudentResponse
from .category import ( 
    InputCategorySchema, 
    ShortResponseCategorySchema,
    FullResponseCategorySchema,
    CategoryPagedResponseSchema,
)
from .course import (
    InputCourseSchema,
    ShortResponseCourseSchema,
    FullResponseCourseSchema,
    CoursePagedResponseSchema,
)
from .other import PagedResponseSchema