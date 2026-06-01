#/bin/bash

# ====================== The-FEFU-Diary Test Setup ======================

BASE_URL="http://localhost"
AUTH_URL="$BASE_URL/api/auth"

STUDENT_EMAIL="newstudent@example.com"
TEACHER_EMAIL="teacher@example.com"
PASSWORD="123456"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== The-FEFU-Diary Test Setup ===${NC}"

echo "→ Регистрация студента..."
curl -X POST $AUTH_URL/register \
    -H "Content-Type: application/json" \
    -d '{
        "email":"'$STUDENT_EMAIL'",
        "password":"'$PASSWORD'",
        "full_name":"Новый Студент",
        "phone":"+7-999-111-2233",
        "group_id":1,
        "student_number":"ST2025002",
        "enrollment_year":2025,
        "birth_date":"2000-01-01",
        "address":"ул. Тестовая"
    }'
echo -e "\n"

echo "→ Назначение роли student..."
docker exec -it university psql -U user -d university_db -c "
    INSERT INTO user_roles (user_id, role_id)
    SELECT u.id, r.id 
    FROM users u, roles r 
    WHERE u.email='$STUDENT_EMAIL' AND r.name='student'
    ON CONFLICT DO NOTHING;
"

echo "→ Регистрация учителя..."
curl -X POST $AUTH_URL/register \
    -H "Content-Type: application/json" \
    -d '{
        "email":"'$TEACHER_EMAIL'",
        "password":"'$PASSWORD'",
        "full_name":"Учитель Тестовый",
        "phone":"+7-999-888-7766",
        "group_id":1,
        "student_number":"TCH001",
        "enrollment_year":2025,
        "birth_date":"1980-01-01",
        "address":""
    }'
echo -e "\n"

echo "→ Назначение роли teacher..."
docker exec -it university psql -U user -d university_db -c "
    INSERT INTO user_roles (user_id, role_id)
    SELECT u.id, r.id FROM users u, roles r 
    WHERE u.email='$TEACHER_EMAIL' AND r.name='teacher'
    ON CONFLICT DO NOTHING;

    INSERT INTO teachers (user_id)
    SELECT id FROM users WHERE email='$TEACHER_EMAIL'
    ON CONFLICT DO NOTHING;
"

echo -e "\n${GREEN}=== Логин студента ===${NC}"
curl -X POST $AUTH_URL/login \
    -H "Content-Type: application/json" \
    -d '{
        "login":"'$STUDENT_EMAIL'",
        "password":"'$PASSWORD'"
    }'

echo -e "\n${GREEN}=== Логин учителя ===${NC}"
curl -X POST $AUTH_URL/login \
    -H "Content-Type: application/json" \
    -d '{
        "login":"'$TEACHER_EMAIL'",
        "password":"'$PASSWORD'"
    }'

echo -e "\n${GREEN}=== Готово! ===${NC}"
echo "Скопируй токен учителя выше и используй его для добавления расписания."