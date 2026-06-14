# Миграции базы данных

SQL-скрипты применяются автоматически при **первом** запуске PostgreSQL (`docker compose up`). Повторный запуск **не** переприменяет их — нужен `docker compose down -v`.

## Порядок файлов

| Файл | Назначение |
|------|------------|
| `01_init.sql` | Схема: users, groups, schedule, grades, attendance |
| `02_seed.sql` | Справочники + demo: роли, группы, аудитории, предметы, преподаватели (Дербенцев, Иванов), расписание ПД, студент Петров |
| `03_students.sql` | 82 студента трёх групп (только users + students, без расписания) |
| `04_grade_scaling.sql` | Категории оценок, шкала, поля raw_score / category_id |
| `05_grade_column_settings.sql` | Типы колонок журнала (ДЗ / КР / ДОП) |

## Разделение ответственности

```
01_init.sql     → структура таблиц
02_seed.sql     → минимальный demo-набор для работы UI (преподаватель + 1 студент + расписание)
03_students.sql → массовая загрузка реальных групп проекта
04–05           → расширения для журнала оценок
```

**Не дублировать** данные между SQL и Python-скриптами — список студентов живёт только в `03_students.sql`.

Дополнительные тестовые учётки через API: `scripts/test-setup.bat`.

## Хеш пароля

Все seed-пользователи с `@student.ru` используют один bcrypt-хеш. Сгенерировать новый:

```bash
python scripts/generate_hash.py mypassword
```

## Пересоздание БД

```bash
docker compose down -v
docker compose up -d
```

## Ручное подключение

```bash
docker exec -it fefu-postgres psql -U user -d university_db
```
