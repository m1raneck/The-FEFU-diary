# Скрипты проекта

Вспомогательные утилиты для разработки и тестирования. **Не используются** при обычном `docker compose up` — данные в БД загружаются из `database/*.sql`.

## Файлы

| Скрипт | Назначение | Когда использовать |
|--------|------------|-------------------|
| `generate_hash.py` | Bcrypt-хеш пароля | Добавляете пользователя в SQL вручную |
| `test-setup.bat` | Регистрация тестового студента и преподавателя через API | Нужны **дополнительные** учётки поверх seed-данных |

## generate_hash.py

```bash
python scripts/generate_hash.py mypassword
```

Вывод — строка для поля `password_hash` в SQL.

Зависимость: `passlib[bcrypt]` (уже есть в auth-service).

## test-setup.bat

```bash
scripts\test-setup.bat
```

Создаёт через API:

- `newstudent@example.com` / `123456` — студент
- `teacher@example.com` / `123456` — преподаватель
