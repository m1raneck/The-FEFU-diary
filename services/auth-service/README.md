# Auth Service

Микросервис аутентификации пользователей (студент/преподаватель) для электронного дневника ДВФУ.

## Как запустить:

1. Клонируй проект, перейди в папку auth-service
2. Скопируй .env.example в .env и укажи свои значения
3. Собери и запусти:
   ```sh
   docker compose up --build auth-service
   ```
Если хочешь запустить без докера сервис (тестировать), то:
   ```sh
   docker-compose up --build db
   cd auth-service
   uvicorn src.<name>:app --reload
   ```
**Фреймворк:** FastAPI
