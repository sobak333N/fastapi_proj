from .user import UserResponse
from .instructor import (
    InstructorResponse, ShortInstructorResponse,
    UpdateInstructorResponse,
)
from .student import (
    StudentResponse, 
    ShortStudentResponse,
    UpdateStudentResponse,
    LessonStudentAnswers,
    LessonStudentAnswerResponse,
    LessonStudentAnswersResponse,
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
    ShortLessonSchema,
    LessonSchema,
    InputLessonSchema,
    UpdateLessonSchema,
    GetLessonSchema,
)
from .lesson_task import (
    LessonTaskSchema,
    InputLessonTaskSchema,
    UpdateLessonTaskSchema,
)
from .other import (
    S3LinkResponse,
    FullTaskMaterial,
    PagedResponseSchema,
    SerializeMaterial,
)