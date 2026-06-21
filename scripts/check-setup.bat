@echo off
chcp 65001 >nul
setlocal

echo =============================================
echo   UniDiary — проверка установки
echo =============================================
echo.

set BASE=http://localhost:8080
set EMAIL=kovalev1@student.ru
set PASS=123456

echo [1] Статус контейнеров:
docker compose ps
echo.

echo [2] Таблица lesson_comments (нужна для страницы оценок):
docker exec fefu-postgres psql -U user -d university_db -c "\dt lesson_comments" 2>nul
if errorlevel 1 (
    echo    ОШИБКА: postgres недоступен
) else (
    echo    OK
)
echo.

echo [3] API через frontend :8080
curl -s -o nul -w "    login: HTTP %%{http_code}\n" -X POST %BASE%/api/auth/login -H "Content-Type: application/json" -d "{\"login\":\"%EMAIL%\",\"password\":\"%PASS%\"}"

for /f "delims=" %%t in ('curl -s -X POST %BASE%/api/auth/login -H "Content-Type: application/json" -d "{\"login\":\"%EMAIL%\",\"password\":\"%PASS%\"}" ^| findstr /C:"token"') do set LOGIN=%%t

curl -s -X POST %BASE%/api/auth/login -H "Content-Type: application/json" -d "{\"login\":\"%EMAIL%\",\"password\":\"%PASS%\"}" > "%TEMP%\diary_login.json" 2>nul

powershell -NoProfile -Command ^
  "$j = Get-Content '%TEMP%\diary_login.json' -Raw | ConvertFrom-Json; " ^
  "if ($j.data.token) { " ^
  "  $h = @{ Authorization = 'Bearer ' + $j.data.token }; " ^
  "  foreach ($ep in @('/api/grades','/api/attendance','/api/lesson-comments')) { " ^
  "    try { $r = Invoke-WebRequest -Uri ('%BASE%' + $ep) -Headers $h -UseBasicParsing; Write-Host ('    ' + $ep + ': HTTP ' + $r.StatusCode) } " ^
  "    catch { Write-Host ('    ' + $ep + ': HTTP ' + $_.Exception.Response.StatusCode.value__) } " ^
  "  } " ^
  "} else { Write-Host '    login failed - check credentials' }"

echo.
echo [4] Версия frontend (не должно быть http://localhost в JS):
docker exec the-fefu-diary-frontend-1 sh -c "grep -q 'http://localhost' /usr/share/nginx/html/assets/index-*.js && echo '    СТАРЫЙ образ! Запустите: docker compose up --build -d' || echo '    OK — новый образ'"

echo.
echo =============================================
echo Если есть ошибки:
echo   git pull
echo   docker compose down
echo   docker compose up --build -d
echo   Откройте http://localhost:8080 и войдите заново
echo.
echo Если БД совсем старая:
echo   docker compose down -v
echo   docker compose up --build -d
echo =============================================
pause
