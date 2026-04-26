# Grades Service

Микросервис оценок (выставление и просмотр) для электронного дневника ДВФУ.

**Как запустить:**
1. Клонируй проект, перейди в папку `grades-service`
2. Скопируй `.env.example` в `.env` и укажи свои значения
3. Собери и запусти:
   ```sh
   docker build -t grades-service .
   docker run -p 8002:8000 --env-file .env grades-service
   ```
4. Фреймворк: FastAPI
