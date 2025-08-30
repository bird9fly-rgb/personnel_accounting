# personnel_accounting/settings/docker.py
"""
Налаштування Django для Docker контейнера
"""
import os
from .base import *

# Отримуємо налаштування з змінних середовища
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', '0') == '1'

# Дозволені хости
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# База даних - використовуємо PostgreSQL в Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'personnel_db'),
        'USER': os.environ.get('DB_USER', 'personnel_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'strongpassword'),
        'HOST': os.environ.get('DB_HOST', 'db'),  # Ім'я сервісу з docker-compose
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Статичні файли
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Медіа файли
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Безпека (для продакшн)
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Встановіть True якщо використовуєте HTTPS
    SESSION_COOKIE_SECURE = False  # Встановіть True якщо використовуєте HTTPS
    CSRF_COOKIE_SECURE = False  # Встановіть True якщо використовуєте HTTPS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Логування
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}