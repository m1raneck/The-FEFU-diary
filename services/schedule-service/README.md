# Schedule Service

Микросервис расписания (уроки, группы) для электронного дневника ДВФУ.

**Как запустить:**
1. Клонируй проект, перейди в папку `schedule-service`
2. Скопируй `.env.example` в `.env` и укажи свои значения
3. Собери и запусти:
   ```sh
   docker build -t schedule-service .
   docker run -p 8001:8000 --env-file .env schedule-service
   ```
4. Фреймворк: FastAPI
