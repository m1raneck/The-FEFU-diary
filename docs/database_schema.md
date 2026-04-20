Схема базы данных
## Сущности (таблицы)

### users
Хранит учётные записи всех пользователей.
- id (SERIAL, PRIMARY KEY) – идентификатор
- email (VARCHAR, UNIQUE) – логин
- password_hash (TEXT) – хеш пароля
- full_name (VARCHAR) – ФИО
- phone (VARCHAR) – телефон
- is_active (BOOLEAN) – активен ли пользователь
- created_at, updated_at (TIMESTAMP)

### roles
Роли пользователей (только teacher и student).
- id (SERIAL, PRIMARY KEY)
- name (VARCHAR, UNIQUE) – название роли
- description (TEXT)

### user_roles
Связь пользователей с ролями (многие ко многим).
- user_id (FK → users.id)
- role_id (FK → roles.id)
- PRIMARY KEY (user_id, role_id)

### students
Расширение для пользователей с ролью student.
- id (SERIAL, PRIMARY KEY)
- user_id (FK → users.id, UNIQUE)
- group_id (FK → groups.id)
- student_number (VARCHAR, UNIQUE) – номер студенческого
- enrollment_year (INTEGER) – год поступления
- birth_date (DATE)
- address (TEXT)

### teachers
Расширение для пользователей с ролью teacher.
- id (SERIAL, PRIMARY KEY)
- user_id (FK → users.id, UNIQUE)
- department (VARCHAR) – кафедра
- position (VARCHAR) – должность
- degree (VARCHAR) – учёная степень

### groups
Учебные группы.
- id (SERIAL, PRIMARY KEY)
- name (VARCHAR, UNIQUE) – например, "101-ИСТ"
- course (INTEGER) – курс (1-6)
- year (INTEGER) – год набора
- created_at (TIMESTAMP)

### subjects
Предметы (дисциплины).
- id (SERIAL, PRIMARY KEY)
- name (VARCHAR, UNIQUE)
- short_name (VARCHAR)
- description (TEXT)
- credits (INTEGER)

### rooms
Аудитории.
- id (SERIAL, PRIMARY KEY)
- number (VARCHAR, UNIQUE)
- building (VARCHAR)
- capacity (INTEGER)

### schedule
Расписание занятий.
- id (SERIAL, PRIMARY KEY)
- group_id (FK → groups.id)
- subject_id (FK → subjects.id)
- teacher_id (FK → teachers.id)
- room_id (FK → rooms.id)
- weekday (INTEGER, 1-7)
- lesson_number (INTEGER, 1-8)
- semester (INTEGER, 1-8)
- year (INTEGER)
- created_at (TIMESTAMP)
- UNIQUE (group_id, weekday, lesson_number, semester, year)

### teacher_subjects
Какие предметы ведёт преподаватель (многие ко многим).
- teacher_id (FK → teachers.id)
- subject_id (FK → subjects.id)
- PRIMARY KEY (teacher_id, subject_id)

### grades
Журнал оценок.
- id (SERIAL, PRIMARY KEY)
- student_id (FK → students.id)
- schedule_id (FK → schedule.id)
- grade (INTEGER, 2-5)
- grade_date (DATE)
- comment (TEXT)
- created_at (TIMESTAMP)
- UNIQUE (student_id, schedule_id, grade_date)

### attendance
Журнал посещаемости.
- id (SERIAL, PRIMARY KEY)
- student_id (FK → students.id)
- schedule_id (FK → schedule.id)
- status (VARCHAR, 'present'/'absent'/'late')
- date (DATE)
- comment (TEXT)
- created_at (TIMESTAMP)
- UNIQUE (student_id, schedule_id, date)