# Документация API

Взаимодействие фронтенда и бэкенда в системе «Электронный дневник» (The-FEFU-diary).

Базовый URL через gateway: `http://localhost/api`

---

## 1. Общие положения

- **Формат:** JSON, UTF-8
- **Авторизация:** `Authorization: Bearer <jwt>` (кроме login/register)
- **Swagger:** каждый сервис отдаёт `/docs` на своём порту (8000–8003)

### Стандартный ответ (auth-service)

```json
{
  "status": "success",
  "data": { },
  "message": null
}
```

Ошибка:

```json
{
  "status": "error",
  "data": null,
  "message": "Описание ошибки"
}
```

> grades, schedule, attendance возвращают Pydantic-модели напрямую (без обёртки `status`).

---

## 2. Auth Service

### POST /api/auth/login

Аутентификация, получение JWT.

**Body:**
```json
{ "login": "student@example.com", "password": "pass123" }
```

**Response:**
```json
{ "status": "success", "data": { "token": "<jwt>" }, "message": "Login successful" }
```

### POST /api/auth/register

Регистрация студента (роль `student` назначается автоматически).

### POST /api/auth/register-teacher

Регистрация преподавателя (роль `teacher` назначается автоматически).

### GET /api/users/me

Профиль текущего пользователя (роли, student_info / teacher_info).

### GET /api/users/students

Список студентов (требует авторизации).

---

## 3. Schedule Service

### GET /api/schedule

Расписание. Фильтры: `group_id`, `teacher_id`, `weekday`.

Студент видит расписание своей группы, преподаватель — свои пары.

### POST /api/schedule

Создание записи расписания (только teacher).

### GET /api/subjects | POST /api/subjects

Список / создание предметов.

### GET /api/rooms | POST /api/rooms

Список / создание аудиторий.

---

## 4. Grades Service

### GET /api/grades

Оценки. Фильтры: `student_id`, `schedule_id`. Студент видит только свои.

### POST /api/grades

Создание/обновление оценки (upsert по student + schedule + date). Teacher only.

**Body:**
```json
{
  "student_id": 1,
  "schedule_id": 5,
  "category_id": 2,
  "raw_score": 85,
  "grade": null,
  "auto_convert": true,
  "grade_date": "2025-03-15",
  "comment": "Отлично"
}
```

### PUT /api/grades/{id} | DELETE /api/grades/{id}

Обновление / удаление оценки.

### POST /api/grades/bulk

Массовое выставление оценок на дату.

### GET /api/grades/categories | PUT /api/grades/categories

Категории оценок (веса) для `schedule_id`.

### GET /api/grades/columns | PUT /api/grades/columns

Типы колонок журнала (ДЗ / КР / ДОП) по датам.

### GET /api/grades/scale | PUT /api/grades/scale

Шкала перевода баллов в оценку 2–5.

### POST /api/grades/convert

Перевод одного балла по шкале.

### POST /api/grades/calculate-final

Расчёт итоговой оценки по взвешенным баллам.

---

## 5. Attendance Service

### GET /api/attendance

Посещаемость. Фильтры: `student_id`, `schedule_id`, `attendance_date`.

### POST /api/attendance

Создание/обновление отметки (upsert). Teacher only.

**Body:**
```json
{
  "student_id": 1,
  "schedule_id": 5,
  "status": "present",
  "record_date": "2025-03-15",
  "comment": null
}
```

Статусы: `present`, `absent`, `late`.

### PUT /api/attendance/{id} | DELETE /api/attendance/{id}

Обновление / удаление записи.

---

## 6. Health

| URL | Сервис |
|-----|--------|
| GET /health (порт 8000) | auth-service |
| GET /health (порт 8001) | attendance-service |
| GET /health (порт 8002) | grades-service |
| GET /health (порт 8003) | schedule-service |
| GET /health/auth (через gateway) | auth-service |
| GET /health/grades (через gateway) | grades-service |

**Response:**
```json
{ "status": "ok", "service": "grades-service", "database": "ok" }
```
