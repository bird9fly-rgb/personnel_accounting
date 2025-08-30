.PHONY: help docker-build docker-up docker-down docker-logs docker-shell docker-migrate docker-test docker-clean docker-restart docker-exec

# Docker команди
help:
	@echo "🐳 DOCKER КОМАНДИ ДЛЯ АСООС 'ОБРІГ':"
	@echo ""
	@echo "  === Основні Docker команди ==="
	@echo "  make docker-build   - 🔨 Збудувати Docker образи"
	@echo "  make docker-up      - 🚀 Запустити всі контейнери"
	@echo "  make docker-down    - 🛑 Зупинити всі контейнери"
	@echo "  make docker-restart - 🔄 Перезапустити контейнери"
	@echo "  make docker-logs    - 📜 Переглянути логи"
	@echo "  make docker-clean   - 🧹 Видалити контейнери та volumes"
	@echo ""
	@echo "  === Робота з Django в Docker ==="
	@echo "  make docker-shell   - 🐚 Відкрити shell в Django контейнері"
	@echo "  make docker-migrate - 🔄 Запустити міграції"
	@echo "  make docker-static  - 📦 Зібрати статичні файли"
	@echo "  make docker-test    - 🧪 Запустити тести"
	@echo "  make docker-exec cmd='...' - 💻 Виконати довільну команду"
	@echo ""
	@echo "  === Управління даними ==="
	@echo "  make docker-loaddata    - 📋 Завантажити початкові дані"
	@echo "  make docker-createsuperuser - 👤 Створити суперкористувача"
	@echo "  make docker-backup  - 💾 Створити backup бази даних"
	@echo "  make docker-restore - 📥 Відновити базу даних з backup"
	@echo ""

# Збудувати Docker образи
docker-build:
	@echo "🔨 Будую Docker образи..."
	docker-compose build

# Запустити всі контейнери
docker-up:
	@echo "🚀 Запускаю всі контейнери..."
	docker-compose up -d
	@echo "✅ Контейнери запущені!"
	@echo ""
	@echo "📌 Доступні адреси:"
	@echo "  Django додаток: http://localhost:8000"
	@echo "  Nginx (якщо увімкнено): http://localhost"
	@echo "  PostgreSQL: localhost:5432"
	@echo ""
	@echo "📊 Адмін панель: http://localhost:8000/admin/"
	@echo "  Логін: admin"
	@echo "  Пароль: admin123"

# Зупинити всі контейнери
docker-down:
	@echo "🛑 Зупиняю всі контейнери..."
	docker-compose down

# Перезапустити контейнери
docker-restart:
	@echo "🔄 Перезапускаю контейнери..."
	docker-compose restart

# Переглянути логи
docker-logs:
	@echo "📜 Показую логи (Ctrl+C для виходу)..."
	docker-compose logs -f

# Логи конкретного сервісу
docker-logs-web:
	docker-compose logs -f web

docker-logs-db:
	docker-compose logs -f db

# Відкрити shell в Django контейнері
docker-shell:
	@echo "🐚 Відкриваю Django shell..."
	docker-compose exec web python manage.py shell_plus --print-sql

# Відкрити bash в контейнері
docker-bash:
	@echo "💻 Відкриваю bash в контейнері..."
	docker-compose exec web /bin/bash

# Запустити міграції
docker-migrate:
	@echo "🔄 Запускаю міграції..."
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

# Зібрати статичні файли
docker-static:
	@echo "📦 Збираю статичні файли..."
	docker-compose exec web python manage.py collectstatic --noinput

# Запустити тести
docker-test:
	@echo "🧪 Запускаю тести..."
	docker-compose exec web python manage.py test

# Виконати довільну команду в контейнері
docker-exec:
	docker-compose exec web $(cmd)

# Створити суперкористувача
docker-createsuperuser:
	@echo "👤 Створення суперкористувача..."
	docker-compose exec web python manage.py createsuperuser

# Завантажити початкові дані
docker-loaddata:
	@echo "📋 Завантажую початкові дані..."
	docker-compose exec web python manage.py loaddata apps/personnel/fixtures/initial_data.json

# Завантажити тестові дані
docker-loadtestdata:
	@echo "📦 Завантажую тестові дані..."
	docker-compose exec web python manage.py create_test_data

# Створити backup бази даних
docker-backup:
	@echo "💾 Створюю backup бази даних..."
	@mkdir -p backups
	docker-compose exec db pg_dump -U personnel_user personnel_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup збережено в backups/"

# Відновити базу даних з backup
docker-restore:
	@echo "📥 Відновлюю базу даних з backup..."
	@echo "Доступні backup файли:"
	@ls -la backups/*.sql
	@read -p "Введіть ім'я файлу для відновлення: " filename; \
	docker-compose exec -T db psql -U personnel_user personnel_db < backups/$$filename

# Повністю очистити Docker середовище
docker-clean:
	@echo "🧹 УВАГА! Це видалить всі контейнери, образи та дані!"
	@read -p "Ви впевнені? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	docker system prune -af
	@echo "✅ Docker середовище очищено"

# Швидкий старт з нуля
docker-fresh-start:
	@echo "🚀 ШВИДКИЙ СТАРТ ПРОЄКТУ В DOCKER"
	@echo "=================================="
	@make docker-clean
	@make docker-build
	@make docker-up
	@sleep 5
	@make docker-migrate
	@make docker-loadtestdata
	@echo "=================================="
	@echo "✅ ПРОЄКТ ГОТОВИЙ ДО РОБОТИ!"
	@echo "=================================="
	@echo "🌐 Відкрийте: http://localhost:8000"
	@echo "📊 Адмін: http://localhost:8000/admin/"
	@echo "👤 Логін: admin / admin123"

# Показати статус контейнерів
docker-ps:
	@echo "📊 Статус контейнерів:"
	docker-compose ps

# Перевірити здоров'я контейнерів
docker-health:
	@echo "🏥 Перевірка здоров'я контейнерів:"
	docker-compose ps
	@echo ""
	@echo "🔍 Перевірка з'єднання з БД:"
	docker-compose exec web python -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1'); print('✅ База даних працює!')"

# Інтерактивна консоль PostgreSQL
docker-dbshell:
	@echo "🗄️ Підключаюся до PostgreSQL..."
	docker-compose exec db psql -U personnel_user -d personnel_db