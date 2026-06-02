@echo off
chcp 65001 >nul

echo =============================================
echo   The-FEFU-Diary Test Setup
echo =============================================

set BASE_URL=http://localhost
set AUTH_URL=%BASE_URL%/api/auth

set STUDENT_EMAIL=newstudent@example.com
set TEACHER_EMAIL=teacher@example.com
set PASSWORD=123456

echo [1] Регистрация студента...
curl -X POST %AUTH_URL%/register ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"%STUDENT_EMAIL%\",\"password\":\"%PASSWORD%\",\"full_name\":\"Новый Студент\",\"phone\":\"+7-999-111-2233\",\"group_id\":1,\"student_number\":\"ST2025002\",\"enrollment_year\":2025,\"birth_date\":\"2000-01-01\",\"address\":\"ул. Тестовая\"}"

echo.
echo [2] Назначение роли student...
docker exec -it university psql -U user -d university_db -c "INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.email='%STUDENT_EMAIL%' AND r.name='student' ON CONFLICT DO NOTHING;"

echo.
echo [3] Регистрация учителя...
curl -X POST %AUTH_URL%/register ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"%TEACHER_EMAIL%\",\"password\":\"%PASSWORD%\",\"full_name\":\"Учитель Тестовый\",\"phone\":\"+7-999-888-7766\",\"group_id\":1,\"student_number\":\"TCH001\",\"enrollment_year\":2025,\"birth_date\":\"1980-01-01\",\"address\":\"\"}"

echo.
echo [4] Назначение роли teacher...
docker exec -it university psql -U user -d university_db -c "INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.email='%TEACHER_EMAIL%' AND r.name='teacher' ON CONFLICT DO NOTHING; INSERT INTO teachers (user_id) SELECT id FROM users WHERE email='%TEACHER_EMAIL%' ON CONFLICT DO NOTHING;"

echo.
echo [5] Логин студента...
curl -X POST %AUTH_URL%/login ^
    -H "Content-Type: application/json" ^
    -d "{\"login\":\"%STUDENT_EMAIL%\",\"password\":\"%PASSWORD%\"}"

echo.
echo [6] Логин учителя...
curl -X POST %AUTH_URL%/login ^
    -H "Content-Type: application/json" ^
    -d "{\"login\":\"%TEACHER_EMAIL%\",\"password\":\"%PASSWORD%\"}"

echo.
echo =============================================
echo Готово!
echo.
echo Скопируй токен учителя из ответа выше и используй его для добавления расписания.
pause