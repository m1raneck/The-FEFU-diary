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

## Если «Ошибка запроса (500)» на странице оценок

Чаще всего — **старая база данных** (нет таблицы `lesson_comments`) или **старый образ frontend**.

```bash
git pull
docker compose down
docker compose up --build -d
```

Проверка: `scripts\check-setup.bat`

Если не помогло — полный сброс БД (удалит все данные):

```bash
docker compose down -v
docker compose up --build -d
```

После этого откройте **http://localhost:8080**, выйдите и войдите заново.

## Полезные команды

```bash
scripts\check-setup.bat         # диагностика (API, БД, версия frontend)
docker compose logs -f
docker exec -it fefu-postgres psql -U user -d university_db
scripts\test-setup.bat          # доп. тестовые учётки через API
python scripts/generate_hash.py # хеш пароля для SQL
```
