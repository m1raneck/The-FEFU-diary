# The-FEFU-diary

Электронный дневник ДВФУ. Проект подгруппы группы РУЦП, 2 курс.

## Быстрый старт

На **любом компьютере** с Docker:

```bash
git clone https://github.com/m1raneck/The-FEFU-diary.git
cd The-FEFU-diary
cp config/.env.example config/.env   # опционально
docker compose up --build -d
```

Дождитесь, пока все контейнеры станут `healthy` (`docker compose ps`).

**Открывайте только:** http://localhost:8080

Тестовые учётки (пароль `123456`): см. [scripts/README.md](scripts/README.md) или seed в `database/`.
После первого запуска можно создать свои через `scripts\test-setup.bat`.

## Структура

```
The-FEFU-diary/
├── config/          # nginx, .env
├── database/        # SQL-скрипты и seed (см. database/README.md)
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
