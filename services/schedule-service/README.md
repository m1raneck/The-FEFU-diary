# Schedule Service

Микросервис расписания (уроки, группы) для электронного дневника ДВФУ.

## Как запустить:

1. Клонируй проект, перейди в папку schedule-service
2. Скопируй .env.example в .env и укажи свои значения
3. Собери и запусти:
   ```sh
   docker compose up --build schedule-service
   ```
Если хочешь запустить без докера сервис (тестировать), то:
   ```sh
   docker compose up --build db
   cd schedule-service
   uvicorn src.<name>:app --reload
   ```
**Фреймворк:** FastAPI
