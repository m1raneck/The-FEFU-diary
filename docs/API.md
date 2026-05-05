# Документация API

Данный документ описывает структуру взаимодействия фронтенда и бэкенда в системе "Электронный дневник" (The-FEFU-diary)

---
## 1. Общие положения
- **Формат данных:** JSON
- **Кодировка:** UTF-8
- **Структура стандартного ответа:**
  ```json
  {
    "status": "success", // или "error"
    "data": { ... },       // объект/массив данных
    "message": null        // строка с сообщением или null
  }
  ```
- **Обработка ошибок:**
  ```json
  {
    "status": "error",
    "data": null,
    "message": "Описание ошибки"
  }
  ```

---
## 2. Эндпоинты по сервисам

### Auth Service

#### POST /api/auth/login
- **Описание:** Аутентификация пользователя и получение токена доступа
- **Request Body:**
  ```json
  {
    "login": "student123",
    "password": "pass123"
  }
  ```
- **Response (успех):**
  ```json
  {
    "status": "success",
    "data": { "token": "<jwt>" },
    "message": null
  }
  ```
- **Response (ошибка):**
  ```json
  {
    "status": "error",
    "data": null,
    "message": "Invalid credentials"
  }
  ```

---
### Grades Service

#### GET /api/grades/my
- **Описание:** Получение списка личных оценок студнета
- **Response:**
  ```json
  {
    "status": "success",
    "data": {
      "grades": [
        { "subject": "Математика", "grade": 4, "comment": "Работа на отлично" }
      ]
    },
    "message": null
  }
  ```

#### POST /api/grades/set
- **Описание:** Преподаватель выставляет оценку и комментарий студенту
- **Request Body:**
  ```json
  {
    "student_id": 123,
    "subject": "Математика",
    "grade": 5,
    "comment": "Потрясающая работа!"
  }
  ```
- **Response (успех):**
  ```json
  {
    "status": "success",
    "data": {},
    "message": "Оценка сохранена"
  }
  ```

---
### Schedule Service

#### GET /api/schedule/weekly
- **Описание:** Получение расписания занятий на текущую неделю (для студента)
- **Response:**
  ```json
  {
    "status": "success",
    "data": {
      "schedule": [
        { "day": "Понедельник", "time": "08:30-10:00", "subject": "Математика", "auditorium": "D212", "teacher": "Иванов И.И." }
      ]
    },
    "message": null
  }
  ```

---
### Attendance Service

#### POST /api/attendance/mark
- **Описание:** Отметка о присутствии на паре (студент/преподаватель)
- **Request Body:**
  ```json
  {
    "student_id": 123,
    "schedule_id": 5,
    "present": true
  }
  ```
- **Response (успех):**
  ```json
  {
    "status": "success",
    "data": {},
    "message": "Посещение отмечено"
  }
  ```

---
