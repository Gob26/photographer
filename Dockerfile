# Используем официальный образ для PostgreSQL
FROM postgres:16

# Устанавливаем переменные окружения для инициализации БД
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Копируем файл для инициализации БД
COPY init.sql /docker-entrypoint-initdb.d/
