# Grades Service

Микросервис оценок (выставление и просмотр) для электронного дневника ДВФУ.

## Как запустить:

1. Клонируй проект, перейди в папку grades-service
2. Скопируй .env.example в .env и укажи свои значения
3. Собери и запусти:
   ```sh
   docker compose up --build grades-service
   ```
Если хочешь запустить без докера сервис (тестировать), то тогда:
   ```sh
   docker compose up --build db
   cd grades-service
   uvicorn src.<name>.py --reload
   ```
**Фреймворк:** FastAPI
