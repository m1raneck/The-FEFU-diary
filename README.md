# The-FEFU-diary

Электронный дневник ДВФУ. Проект подгруппы группы РУЦП, 2 курс.

## Быстрый старт

```bash
cd The-FEFU-diary
cp config/.env.example config/.env
docker compose up --build -d
```

- **UI:** http://localhost:8080
- **API:** http://localhost/api

## Структура

```
The-FEFU-diary/
├── config/          # nginx, .env
├── database/        # SQL-миграции и seed (см. database/README.md)
├── docs/            # документация API и схемы БД
├── frontend/        # Vue 3 SPA
├── scripts/         # утилиты для разработки (см. scripts/README.md)
├── services/        # микросервисы + fefu_common
└── docker-compose.yml
```

## Документация

- [database/README.md](database/README.md) — порядок SQL-миграций
- [scripts/README.md](scripts/README.md) — вспомогательные скрипты
- [docs/API.md](docs/API.md) — эндпоинты
- [TEACHER_INSTRUCTIONS.md](TEACHER_INSTRUCTIONS.md) — инструкция для преподавателя

## Полезные команды

```bash
docker compose logs -f
docker exec -it fefu-postgres psql -U user -d university_db
scripts\test-setup.bat          # доп. тестовые учётки через API
python scripts/generate_hash.py # хеш пароля для SQL
```
