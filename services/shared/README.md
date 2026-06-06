# Shared

Общие утилиты и библиотеки для микросервисов проекта.

## fefu_common

Пакет `fefu_common` содержит переиспользуемый код:

- `config` — настройки из переменных окружения (DATABASE_URL, SECRET_KEY, JWT)
- `database` — фабрика подключения к PostgreSQL с пулом соединений
- `auth` — единая JWT-авторизация и проверка ролей
- `tokens` — создание access-токенов
- `health` — эндпоинт `/health` для мониторинга

Подключается в Docker через `PYTHONPATH=/app` и копирование `services/shared/src/fefu_common`.
