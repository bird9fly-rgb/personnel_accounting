.PHONY: help up down logs install run migrate makemigrations superuser shell test fresh-start load-test-data load-fixtures quick-start

# Використовуємо .env файл для змінних
include .env
export

help:
	@echo "Доступні команди для управління проєктом АСООС 'ОБРІГ':"
	@echo ""
	@echo "  === Основні команди ==="
	@echo "  make quick-start    - 🚀 ШВИДКИЙ СТАРТ: запускає БД, міграції, створює адміна і тестові дані."
	@echo "  make up             - Запустити контейнер з базою даних у фоновому режимі."
	@echo "  make down           - Зупинити контейнер з базою даних."
	@echo "  make logs           - Переглянути логи бази даних в реальному часі."
	@echo "  make install        - Встановити залежності Python з requirements.txt."
	@echo "  make run            - Запустити локальний сервер розробки Django."
	@echo ""
	@echo "  === Робота з БД та міграціями ==="
	@echo "  make migrate        - Застосувати міграції до бази даних."
	@echo "  make makemigrations - Створити нові файли міграцій на основі змін у моделях."
	@echo "  make superuser      - Створити нового суперкористувача (адміністратора)."
	@echo "  make shell          - Запустити розширену оболонку Django (shell_plus)."
	@echo ""
	@echo "  === Тестові дані ==="
	@echo "  make load-test-data - 📦 Завантажити повний набір тестових даних (підрозділи, персонал, контракти)."
	@echo "  make load-fixtures  - 📋 Завантажити базові дані з fixtures (звання, ВОС)."
	@echo ""
	@echo "  === Розробка та тестування ==="
	@echo "  make test           - Запустити тести для проєкту."
	@echo "  make fresh-start    - 🔥 ПОВНІСТЮ ВИДАЛИТИ БАЗУ ДАНИХ та почати з нуля."
	@echo ""
	@echo "  === Корисні команди ==="
	@echo "  make check-deploy   - Перевірити готовність проєкту до deployment."
	@echo "  make show-urls      - Показати всі доступні URL проєкту."
	@echo "  make db-shell       - Підключитися до консолі PostgreSQL."
	@echo ""

up:
	@echo "🚀 Запускаю контейнер з базою даних PostgreSQL..."
	docker-compose up -d
	@echo "✅ База даних запущена. Очікую готовності..."
	@sleep 3

down:
	@echo "🛑 Зупиняю контейнер з базою даних..."
	docker-compose down

logs:
	@echo "📜 Переглядаю логи бази даних..."
	docker-compose logs -f db

install:
	@echo "📦 Встановлюю залежності Python..."
	pip install -r requirements.txt
	@echo "✅ Залежності встановлено"

run:
	@echo "🌐 Запускаю сервер розробки Django на http://127.0.0.1:8000/"
	@echo "📊 Адмін панель: http://127.0.0.1:8000/admin/"
	@echo "👥 Особовий склад: http://127.0.0.1:8000/"
	@echo "🏢 Підрозділи: http://127.0.0.1:8000/staffing/"
	python manage.py runserver

migrate:
	@echo "🔄 Застосовую міграції бази даних..."
	python manage.py migrate
	@echo "✅ Міграції застосовано"

makemigrations:
	@echo "📝 Створюю нові міграції..."
	python manage.py makemigrations
	@echo "✅ Міграції створено"

superuser:
	@echo "👤 Створення суперкористувача..."
	@echo "Використовуйте наступні дані для тестування:"
	@echo "  Username: admin"
	@echo "  Password: admin123"
	@echo "  Email: admin@mil.gov.ua"
	python manage.py createsuperuser

shell:
	@echo "🐚 Запускаю Django shell..."
	python manage.py shell_plus --print-sql

test:
	@echo "🧪 Запускаю тести..."
	python manage.py test

fresh-start:
	@echo "🔥 УВАГА! Це видалить всі дані з бази даних!"
	@read -p "Ви впевнені? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "🗑️ Видаляю контейнер та дані..."
	docker-compose down -v
	@echo "✅ Дані видалено. Запускаю нову базу даних..."
	@make up
	@sleep 5
	@echo "📝 Застосовую міграції..."
	@make migrate
	@echo "✅ База даних готова до роботи!"

load-test-data:
	@echo "📦 Завантажую тестові дані..."
	@echo "Це створить:"
	@echo "  • Військові звання (21 звання)"
	@echo "  • Військово-облікові спеціальності (20 ВОС)"
	@echo "  • Структуру підрозділів (бригада з батальйонами, ротами, взводами)"
	@echo "  • Штатні посади (~500 посад)"
	@echo "  • Військовослужбовців (70% укомплектованість)"
	@echo "  • Контракти та історію служби"
	@echo ""
	@echo "⏳ Це може зайняти кілька хвилин..."
	python manage.py create_test_data
	@echo "✅ Тестові дані завантажено!"

load-fixtures:
	@echo "📋 Завантажую базові дані з fixtures..."
	@mkdir -p apps/personnel/fixtures
	@echo "Створюю fixtures для звань та ВОС..."
	python manage.py loaddata apps/personnel/fixtures/initial_data.json
	@echo "✅ Fixtures завантажено"

quick-start:
	@echo "🚀 ШВИДКИЙ СТАРТ ПРОЄКТУ АСООС 'ОБРІГ'"
	@echo "======================================="
	@echo "Крок 1: Запуск бази даних..."
	@make up
	@echo ""
	@echo "Крок 2: Встановлення залежностей..."
	@make install
	@echo ""
	@echo "Крок 3: Застосування міграцій..."
	@make migrate
	@echo ""
	@echo "Крок 4: Створення адміністратора..."
	@echo "Створюю користувача admin з паролем admin123..."
	@echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@mil.gov.ua', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
	@echo ""
	@echo "Крок 5: Завантаження тестових даних..."
	@make load-test-data
	@echo ""
	@echo "======================================="
	@echo "✅ ПРОЄКТ ГОТОВИЙ ДО РОБОТИ!"
	@echo "======================================="
	@echo ""
	@echo "📌 Облікові записи для входу:"
	@echo "  Адміністратор:   admin / admin123"
	@echo "  Кадровий офіцер: hr_officer / hr123"
	@echo "  Командир:        commander / commander123"
	@echo ""
	@echo "🌐 Для запуску сервера виконайте: make run"
	@echo "📊 Адмін панель: http://127.0.0.1:8000/admin/"
	@echo ""

check-deploy:
	@echo "🔍 Перевірка готовності до deployment..."
	python manage.py check --deploy
	@echo "✅ Перевірка завершена"

show-urls:
	@echo "📍 Доступні URL адреси:"
	python manage.py show_urls

db-shell:
	@echo "🗄️ Підключаюся до PostgreSQL..."
	docker exec -it asoos_postgres_db psql -U $(DB_USER) -d $(DB_NAME)