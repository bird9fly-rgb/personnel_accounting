#!/bin/sh

set -e

echo "Waiting for PostgreSQL to be ready..."

# Чекаємо поки база даних стане доступною
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
    echo "Waiting for database connection at ${DB_HOST:-db}:${DB_PORT:-5432}..."
    sleep 2
done

echo "PostgreSQL is ready!"

# Застосовуємо міграції
echo "Applying database migrations..."
python manage.py migrate --noinput

# Збираємо статичні файли
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Створюємо суперкористувача якщо не існує
echo "Creating superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created!')
else:
    print('Superuser already exists.')
EOF

# Завантажуємо початкові дані (якщо потрібно)
if [ "$LOAD_TEST_DATA" = "1" ]; then
    echo "Loading test data..."
    python manage.py loaddata apps/personnel/fixtures/initial_data.json || true
    python manage.py create_test_data || true
fi

echo "Starting application..."
exec "$@"