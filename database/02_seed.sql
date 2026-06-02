INSERT INTO roles (name, description) VALUES
    ('teacher', 'Преподаватель'),
    ('student', 'Студент')
ON CONFLICT (name) DO NOTHING;

-- Добавляем группы для расписания преподавателя
INSERT INTO groups (name, course, year) VALUES
    ('101-ИСТ', 1, 2024),
    ('102-ПИ', 1, 2024),
    ('103-ЭК', 1, 2024),
    ('201-ИСТ', 2, 2023),
    ('202-ПИ', 2, 2023),
    ('Б9124-09.03.03ру', 3, 2024),
    ('Б9125-09.03.04ру', 3, 2024),
    ('Б9125-02.03.01мо', 2, 2024)
ON CONFLICT (name) DO NOTHING;

INSERT INTO rooms (number, building, capacity) VALUES
    ('101', 'Главный корпус', 30),
    ('102', 'Главный корпус', 25),
    ('201', 'Главный корпус', 40),
    ('301', 'Лабораторный корпус', 20),
    ('401', 'Лабораторный корпус', 15),
    ('D547', 'Корпус D', 31),
    ('D740', 'Корпус D', 26),
    ('D945', 'Корпус D', 25),
    ('408', 'Корпус D', 30),
    ('215', 'Главный корпус', 25)
ON CONFLICT (number) DO NOTHING;

INSERT INTO subjects (name, short_name, description, credits) VALUES
    ('Математический анализ', 'Матан', 'Пределы, производные, интегралы', 5),
    ('Базы данных', 'БД', 'SQL, проектирование, нормализация', 4),
    ('Программирование на Python', 'Python', 'Основы Python, ООП, алгоритмы', 4),
    ('Физика', 'Физика', 'Механика, электричество', 4),
    ('Английский язык', 'Англ', 'Профессиональный английский', 3),
    ('Проектная деятельность', 'ПД', 'Выполнение проектных работ', 3)
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, phone)
SELECT 'ivanov@university.ru', '$2b$12$gSvqqUPHQ.cIvV2dWK3UKOYm8sIErGhXGLVbF5DhDiNn.3NhF5jBi', 'Иванов Иван Иванович', '+7-900-222-3344'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'ivanov@university.ru');

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.email = 'ivanov@university.ru' AND r.name = 'teacher'
ON CONFLICT DO NOTHING;

INSERT INTO teachers (user_id, department, position, degree)
SELECT id, 'Факультет информатики', 'Доцент', 'к.ф.-м.н.' FROM users WHERE email = 'ivanov@university.ru'
ON CONFLICT (user_id) DO NOTHING;

-- Добавляем преподавателя Дербенцева
INSERT INTO users (email, password_hash, full_name, phone)
SELECT 'derbentcev.no@dvfu.ru', '$2b$12$QIpVcjOBDPUYYfHLMjlFduUfj.GNQpBFSWJXD2Y9MjCVUYKYBYHnq', 'Дербенцев Н.О.', '+7-900-100-0001'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'derbentcev.no@dvfu.ru');

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.email = 'derbentcev.no@dvfu.ru' AND r.name = 'teacher'
ON CONFLICT DO NOTHING;

INSERT INTO teachers (user_id, department, position, degree)
SELECT id, 'Факультет информатики', 'Преподаватель', 'м.и.' FROM users WHERE email = 'derbentcev.no@dvfu.ru'
ON CONFLICT (user_id) DO NOTHING;

-- Расписание для преподавателя Дербенцева
-- Вторник, 10:10 - 11:40, Б9124-09.03.03ру, D547
INSERT INTO schedule (group_id, subject_id, teacher_id, room_id, weekday, lesson_number, semester, year)
SELECT g.id, s.id, t.id, r.id, 2, 2, 1, 2026
FROM groups g CROSS JOIN subjects s CROSS JOIN teachers t CROSS JOIN rooms r
WHERE g.name = 'Б9124-09.03.03ру' AND s.name = 'Проектная деятельность'
  AND EXISTS (SELECT 1 FROM users u WHERE u.email = 'derbentcev.no@dvfu.ru' AND t.user_id = u.id)
  AND r.number = 'D547'
ON CONFLICT DO NOTHING;

-- Вторник, 11:50 - 13:20, Б9125-09.03.04ру, D740
INSERT INTO schedule (group_id, subject_id, teacher_id, room_id, weekday, lesson_number, semester, year)
SELECT g.id, s.id, t.id, r.id, 2, 3, 1, 2026
FROM groups g CROSS JOIN subjects s CROSS JOIN teachers t CROSS JOIN rooms r
WHERE g.name = 'Б9125-09.03.04ру' AND s.name = 'Проектная деятельность'
  AND EXISTS (SELECT 1 FROM users u WHERE u.email = 'derbentcev.no@dvfu.ru' AND t.user_id = u.id)
  AND r.number = 'D740'
ON CONFLICT DO NOTHING;

-- Суббота, 10:10 - 11:40, Б9125-02.03.01мо, D945
INSERT INTO schedule (group_id, subject_id, teacher_id, room_id, weekday, lesson_number, semester, year)
SELECT g.id, s.id, t.id, r.id, 6, 2, 1, 2026
FROM groups g CROSS JOIN subjects s CROSS JOIN teachers t CROSS JOIN rooms r
WHERE g.name = 'Б9125-02.03.01мо' AND s.name = 'Проектная деятельность'
  AND EXISTS (SELECT 1 FROM users u WHERE u.email = 'derbentcev.no@dvfu.ru' AND t.user_id = u.id)
  AND r.number = 'D945'
ON CONFLICT DO NOTHING;

INSERT INTO users (email, password_hash, full_name, phone)
SELECT 'petrov@student.ru', '$2b$12$wXp11PgvF2xiwaw0BkqdOuXd/Q2fahznvMJhd88L9xLvKY3U3XK56', 'Петров Петр Петрович', '+7-900-333-4455'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'petrov@student.ru');

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.email = 'petrov@student.ru' AND r.name = 'student'
ON CONFLICT DO NOTHING;

INSERT INTO students (user_id, group_id, student_number, enrollment_year, birth_date)
SELECT u.id, g.id, '2024-001', 2024, '2005-05-15'
FROM users u, groups g WHERE u.email = 'petrov@student.ru' AND g.name = '101-ИСТ'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t JOIN users u ON t.user_id = u.id CROSS JOIN subjects s
WHERE u.email = 'ivanov@university.ru' AND s.name = 'Базы данных'
ON CONFLICT DO NOTHING;

INSERT INTO schedule (group_id, subject_id, teacher_id, room_id, weekday, lesson_number, semester, year)
SELECT g.id, s.id, t.id, r.id, 1, 1, 1, 2024
FROM groups g CROSS JOIN subjects s CROSS JOIN teachers t CROSS JOIN rooms r
WHERE g.name = '101-ИСТ' AND s.name = 'Базы данных'
  AND EXISTS (SELECT 1 FROM users u WHERE u.email = 'ivanov@university.ru' AND t.user_id = u.id)
  AND r.number = '301'
ON CONFLICT DO NOTHING;

INSERT INTO grades (student_id, schedule_id, grade, grade_date)
SELECT s.id, sch.id, 5, '2024-09-15'
FROM students s JOIN users u ON s.user_id = u.id CROSS JOIN schedule sch
WHERE u.email = 'petrov@student.ru' AND sch.year = 2024 AND sch.semester = 1
  AND EXISTS (SELECT 1 FROM subjects sub WHERE sub.name = 'Базы данных' AND sch.subject_id = sub.id)
ON CONFLICT DO NOTHING;

INSERT INTO attendance (student_id, schedule_id, status, date)
SELECT s.id, sch.id, 'present', '2024-09-15'
FROM students s JOIN users u ON s.user_id = u.id CROSS JOIN schedule sch
WHERE u.email = 'petrov@student.ru' AND sch.year = 2024 AND sch.semester = 1
  AND EXISTS (SELECT 1 FROM subjects sub WHERE sub.name = 'Базы данных' AND sch.subject_id = sub.id)
ON CONFLICT DO NOTHING;
