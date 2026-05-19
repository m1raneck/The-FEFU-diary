# Стадия сборки (именно AS build)
FROM node:18-alpine AS build

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./
RUN npm ci

# Копируем исходники и собираем приложение
COPY . .
RUN npm run build

# Стадия отдачи статики через Nginx
FROM nginx:alpine

# Копируем собранные файлы из стадии build
COPY --from=build /app/dist /usr/share/nginx/html

# Добавляем конфиг с fallback для SPA (чтобы роутинг работал)
RUN echo 'server { listen 80; location / { root /usr/share/nginx/html; try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]