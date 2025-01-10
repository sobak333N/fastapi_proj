INSERT INTO users (email, first_name, second_name, last_name, birthdate, password_hash,created_at, role)
VALUES
('student1@ya.ru', 'John', 'A.', 'Doe', '1990-01-01', 'Q1w2e3r4-',NOW() , 'student'),
('student2@ya.ru', 'Jane', 'B.', 'Smith', '1992-02-02', 'Q1w2e3r4-',NOW() , 'student'),
('instructor1@ya.ru', 'Peter', 'C.', 'Parker', '1985-03-03', 'Q1w2e3r4-', NOW() , 'instructor'),
('instructor2@ya.ru', 'Tony', 'D.', 'Stark', '1975-04-04', 'Q1w2e3r4-', NOW() , 'instructor'),
('student3@ya.ru', 'Natasha', 'E.', 'Romanoff', '1988-05-05', 'Q1w2e3r4-', NOW() , 'student'),
('student4@ya.ru', 'Bruce', 'F.', 'Banner', '1980-06-06', 'Q1w2e3r4-', NOW() , 'instructor');


INSERT INTO instructors (user_id, education, academic_degree, academical_experience, "H_index")
VALUES
(3, 'MIT', 'master', 10, NULL),
(4, 'Harvard', 'master', 15, NULL);


INSERT INTO students (user_id, subscription_plan, learning_style)
VALUES
(1, 'free', 'visual'),
(2, 'free', 'visual'),
(5, 'free', 'visual'),
(6, 'free', 'visual');

INSERT INTO category (category_name, category_description, keywords)
VALUES 
('category1', 'category1_desc', 'category1_keywords');

INSERT INTO course (instructor_id, category_id, course_name, cost, difficulty, private_info)
VALUES
(1, 1, 'course1', 2000, 'easy', 'private_info1');

INSERT INTO student_course (course_id, student_id, payment_type, payment_status, progress, finished, start_date, end_date)
VALUES 
(1, 1, 'card', 'in_progress', NULL, NULL, NULL, NULL),
(1, 2, 'card', 'done', NULL, NULL, NULL, NULL);