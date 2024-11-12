# Используем официальный Python образ
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y supervisor\
    build-essential \
    meson \
    pkg-config \
    python3-dev \
    libdbus-1-dev && \
    pip install -r requirements.txt

# Копируем все файлы проекта
COPY . /app

# Открываем порт 5000 для доступа к приложению Flask
EXPOSE 5000

# Запуск Flask-приложения и Telegram-бота через Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]


