# Схема базы данных

PostgreSQL, база `university_db`. ER-описание таблиц и связей.

## Сущности

### users
Учётные записи.
- `id` SERIAL PK
- `email` VARCHAR UNIQUE — логин
- `password_hash` TEXT
- `full_name` VARCHAR
- `phone` VARCHAR

### roles / user_roles
Роли (`student`, `teacher`) и связь многие-ко-многим с users.

### students
Профиль студента: `user_id`, `group_id`, `student_number`, `enrollment_year`, `birth_date`, `address`.

### teachers
Профиль преподавателя: `user_id`, `department`, `position`, `degree`.

### groups
Учебные группы: `name`, `course` (1–6), `year`.

### subjects
Дисциплины: `name`, `short_name`, `description`, `credits`.

### rooms
Аудитории: `number`, `building`, `capacity`.

### schedule
Расписание: `group_id`, `subject_id`, `teacher_id`, `room_id`, `weekday` (1–7), `lesson_number` (1–8), `semester`, `year`.

UNIQUE (`group_id`, `weekday`, `lesson_number`, `semester`, `year`).

### teacher_subjects
Связь преподаватель ↔ предмет (M:N).

### grade_categories
Категории оценок для пары: `schedule_id`, `code`, `name`, `weight`.

UNIQUE (`schedule_id`, `code`).

### grade_scale_rules
Шкала баллов → оценка: `schedule_id`, `min_points`, `max_points`, `final_grade` (2–5).

### grade_column_settings
Тип колонки журнала на дату: `schedule_id`, `grade_date`, `column_type` (ДЗ / КР / ДОП).

UNIQUE (`schedule_id`, `grade_date`).

### grades
Журнал оценок.
- `student_id`, `schedule_id`, `category_id` (nullable)
- `grade` INTEGER (0–100 или 2–5)
- `raw_score` NUMERIC — исходный балл
- `grade_date` DATE
- `comment` TEXT

UNIQUE (`student_id`, `schedule_id`, `grade_date`).

### attendance
Журнал посещаемости: `student_id`, `schedule_id`, `status` (`present`/`absent`/`late`), `date`, `comment`.

UNIQUE (`student_id`, `schedule_id`, `date`).

## Связи

- user → student **или** teacher (1:1)
- student → group (N:1)
- schedule → group, subject, teacher, room
- grades / attendance → student + schedule
- grade_categories / grade_scale_rules / grade_column_settings → schedule

## Индексы

Создаются в `01_init.sql` и миграциях `04`, `05` — по `email`, `group_id`, `schedule_id`, `student_id`, `grade_date`.
