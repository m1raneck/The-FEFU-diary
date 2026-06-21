@echo off
chcp 65001 >nul

echo =============================================
echo   The-FEFU-Diary Test Setup
echo =============================================
echo Требуется запущенный docker compose up
echo.

set BASE_URL=http://localhost
set AUTH_URL=%BASE_URL%/api/auth

set STUDENT_EMAIL=newstudent@example.com
set TEACHER_EMAIL=teacher@example.com
set PASSWORD=123456

echo [1] Регистрация студента...
curl -s -X POST %AUTH_URL%/register ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"%STUDENT_EMAIL%\",\"password\":\"%PASSWORD%\",\"full_name\":\"Новый Студент\",\"phone\":\"+7-999-111-2233\",\"group_id\":1,\"student_number\":\"ST2025002\",\"enrollment_year\":2025,\"birth_date\":\"2000-01-01\",\"address\":\"ул. Тестовая\"}"

echo.
echo [2] Регистрация преподавателя...
curl -s -X POST %AUTH_URL%/register-teacher ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"%TEACHER_EMAIL%\",\"password\":\"%PASSWORD%\",\"full_name\":\"Учитель Тестовый\",\"phone\":\"+7-999-888-7766\",\"department\":\"ИИТ\",\"position\":\"доцент\",\"degree\":\"к.т.н.\"}"

echo.
echo [3] Логин студента...
curl -s -X POST %AUTH_URL%/login ^
    -H "Content-Type: application/json" ^
    -d "{\"login\":\"%STUDENT_EMAIL%\",\"password\":\"%PASSWORD%\"}"

echo.
echo [4] Логин преподавателя...
curl -s -X POST %AUTH_URL%/login ^
    -H "Content-Type: application/json" ^
    -d "{\"login\":\"%TEACHER_EMAIL%\",\"password\":\"%PASSWORD%\"}"

echo.
echo =============================================
echo Готово! Роли назначаются автоматически при регистрации.
echo Скопируй токен преподавателя для работы с расписанием и оценками.
pause
