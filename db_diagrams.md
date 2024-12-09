// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs


Table users {
  user_id integer [primary key]
  username varchar
  first_name varchar
  second_name varchar
  last_name varchar
  birthdate varchar
  passw_hash varchar
  created_at timestamp
}

Table students {
  student_id integer [primary key]
  user_id integer 
  group_id integer
  avg_score float
}

Table instructors {
  instructor_id integer [primary key]
  user_id integer
  education varchar
  academic_degree enum
  academical_experience integer
  H_index float
}

Table categories {
  category_id integer [primary key]
  category_name varchar
}


Table courses {
  course_id integer [primary key]
  instructor_id integer
  category_id integer
  cost integer
  difficulty enum
}

Table student_courses {
  student_course_id integer [primary key]
  course_id integer
  student_id integer
  payment_type enum
  payment_status enum
  progress float
}

Table lessons {
  lesson_id integer [primary key]
  course_id integer 
  lesson_materials varchar
}

Table student_lesson {
  student_lesson_id integer [primary key]
  student_course_id integer 
  lesson_id integer [primary key]
  done bool
  result integer
}

Table lesson_tasks {
  lesson_task_id integer [primary key]
  lesson_id integer 
  question varchar
  answers list(varchar)
  answer varchar
}

Table lesson_task_student {
  lesson_task_student_id integer [primary key]
  student_lesson_id integer 
  lesson_task_id integer 
  answer varchar
  correct bool
}


Ref: users.user_id - students.user_id // one-to-one
Ref: users.user_id - instructors.user_id // one-to-one
Ref: instructors.instructor_id < courses.instructor_id // many-to-one
Ref: categories.category_id < courses.category_id // many-to-one
Ref: students.student_id < student_courses.student_id // many-to-one
Ref: courses.course_id < student_courses.course_id // many-to-one
Ref: courses.course_id < lessons.course_id // many-to-one
Ref: lessons.lesson_id < student_lesson.lesson_id // many-to-one
Ref: student_courses.student_course_id < student_lesson.student_course_id // many-to-one
Ref: lessons.lesson_id < lesson_tasks.lesson_id // many-to-one
Ref: lesson_tasks.lesson_task_id < lesson_task_student.lesson_task_id // many-to-one
Ref: student_lesson.student_lesson_id < lesson_task_student.student_lesson_id // many-to-one




