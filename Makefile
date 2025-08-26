.PHONY: help up down logs install run migrate makemigrations superuser shell test fresh-start

# Використовуємо .env файл для змінних
include .env
export

help:
	@echo "Доступні команди для управління проєктом АСООС 'ОБРІГ':"
	@echo ""
	@echo "  make up             - Запустити контейнер з базою даних у фоновому режимі."
	@echo "  make down           - Зупинити контейнер з базою даних."
	@echo "  make logs           - Переглянути логи бази даних в реальному часі."
	@echo "  make install        - Встановити залежності Python з requirements.txt."
	@echo "  make run            - Запустити локальний сервер розробки Django."
	@echo "  make migrate        - Застосувати міграції до бази даних."
	@echo "  make makemigrations - Створити нові файли міграцій на основі змін у моделях."
	@echo "  make superuser      - Створити нового суперкористувача (адміністратора)."
	@echo "  make shell          - Запустити розширену оболонку Django (shell_plus)."
	@echo "  make test           - Запустити тести для проєкту."
	@echo "  make fresh-start    - 🔥 ПОВНІСТЮ ВИДАЛИТИ БАЗУ ДАНИХ та почати з нуля."
	@echo ""

up:
	@echo "🚀 Запускаю контейнер з базою даних PostgreSQL..."
	docker-compose up -d

down:
	@echo "🛑 Зупиняю контейнер з базою даних..."
	docker-compose down

logs:
	@echo "📜 Переглядаю логи бази даних..."
	docker-compose logs -f db

install:
	@echo "📦 Встановлюю залежності Python..."
	pip install -r requirements.txt

run:
	@echo "🌐 Запускаю сервер розробки Django на http://127.0.0.1:8000/"
	python manage.py runserver

migrate:
	@echo "Applying database migrations..."
	python manage.py migrate

makemigrations:
	@echo "Creating new migrations..."
	python manage.py makemigrations

superuser:
	@echo "Creating superuser..."
	python manage.py createsuperuser

shell:
	@echo "Starting Django shell..."
	python manage.py shell_plus --print-sql

test:
	@echo "Running tests..."
	python manage.py test

fresh-start:
	@echo "🔥 Повністю видаляю дані бази даних..."
	docker-compose down -v
	@echo "✅ Дані бази видалено. Тепер можна почати з 'make up'."