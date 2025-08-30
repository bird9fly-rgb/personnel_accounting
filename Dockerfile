# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо та встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копіюємо код проекту
COPY . .

# Створюємо директорії для статичних файлів
RUN mkdir -p /app/staticfiles /app/media

# Створюємо непривілейованого користувача
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Відкриваємо порт
EXPOSE 8000

# Команда за замовчуванням
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi:application"]