# Attendance Service

Микросервис посещаемости (отметки пар) для электронного дневника ДВФУ.

**Как запустить:**
1. Клонируй проект, перейди в папку `attendance-service`
2. Скопируй `.env.example` в `.env` и укажи свои значения
3.1 Собери и запусти:
   ```sh
   docker up --build attendance-service
   ```
3.2 Если хочешь запусить без докера сервис(тестировать), то тогда:
   ```sh
   docker up --build db
   cd attendance-service
   uvicorn src.<name>.py --reload
   ```
4. Фреймворк: FastAPI
