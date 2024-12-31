from .user import UserResponse
from .instructor import (
    InstructorResponse, ShortInstructorResponse,
    UpdateInstructorResponse,
)
from .student import (
    StudentResponse, 
    ShortStudentResponse,
    UpdateStudentResponse,
)
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
    PrivateResponseCourseSchema,
)
from .lesson import (
    LessonSchema,
    InputLessonSchema,
    UpdateLessonSchema,
)
from .lesson_task import (
    LessonTaskSchema,
    InputLessonTaskSchema,
)
from .other import PagedResponseSchema