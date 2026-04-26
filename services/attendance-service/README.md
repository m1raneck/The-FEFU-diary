# Attendance Service

Микросервис посещаемости (отметки пар) для электронного дневника ДВФУ.

**Как запустить:**
1. Клонируй проект, перейди в папку `attendance-service`
2. Скопируй `.env.example` в `.env` и укажи свои значения
3. Собери и запусти:
   ```sh
   docker build -t attendance-service .
   docker run -p 8003:8000 --env-file .env attendance-service
   ```
4. Фреймворк: FastAPI
