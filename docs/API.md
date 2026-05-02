# Документация API

Данный документ описывает структуру взаимодействия фронтенда и бэкенда в системе "Электронный дневник" (The-FEFU-diary), стандарты передачи данных, спецификацию эндпоинтов и примеры запросов/ответов.

---
## 1. Общие положения
- **Формат данных:** JSON
- **Кодировка:** UTF-8
- **Аутентификация:** Все защищённые запросы требуют заголовка `Authorization: Bearer <jwt>`
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
- **Описание:** Аутентификация пользователя и получение access-токена (JWT)
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
- **Описание:** Получение списка личных оценок (студент)
- **Заголовки:** `Authorization: Bearer <jwt>`
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
- **Заголовки:** `Authorization: Bearer <jwt>`
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
- **Заголовки:** `Authorization: Bearer <jwt>`
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
- **Заголовки:** `Authorization: Bearer <jwt>`
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
## 3. Примеры curl-запросов

### Пример: Вход пользователя
```bash
curl -X POST https://<host>/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"login":"student123","password":"pass123"}'
```

---
## 4. Коды ошибок
- Неавторизован: 401 Unauthorized
- Отсутствуют обязательные данные: 400 Bad Request
- Не найдено: 404 Not Found

---
## 5. Замечания по расширяемости
- Все сервисы поддерживают расширение набора эндпоинтов по аналогии с представленными.
- Общая структура ответа строго сохраняется для удобства фронтенд-разработки и тестирования.
