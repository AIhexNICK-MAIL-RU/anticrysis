# ========== Stage 1: сборка фронтенда ==========
FROM node:20-alpine AS frontend-builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ========== Stage 2: продакшен-образ (бэкенд + nginx + статика) ==========
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Бэкенд
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/

# Статика фронтенда из stage 1
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Nginx: раздаёт статику и проксирует /api на бэкенд
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
    location /api/ { \
        rewrite ^/api(.*)$ $1 break; \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Каталог для БД (при запуске можно смонтировать volume: -v anticrisis_data:/app/backend/data)
RUN mkdir -p /app/backend/data
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite+aiosqlite:///./data/anticrisis.db

EXPOSE 80

# Запуск: uvicorn в фоне, nginx на переднем плане
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
CMD ["/docker-entrypoint.sh"]
