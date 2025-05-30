FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для psycopg2 и других пакетов
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Копируем .env файл (если он есть)
COPY .env .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 