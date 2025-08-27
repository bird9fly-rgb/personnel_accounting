import os
import textwrap

# ==============================================================================
# КОНФІГУРАЦІЯ ГЕНЕРАТОРА
# Тут ми визначаємо структуру та вміст файлів нашого проєкту Django.
# ==============================================================================

PROJECT_NAME = "personnel_accounting"
APPS_DIR = "apps"
APP_NAMES = ["core", "users", "staffing", "personnel", "reporting", "auditing"]

# Словник, що містить шляхи до файлів та їхній вміст
project_files = {
    # --- Файли в кореневій папці проєкту ---
    "manage.py": """
    #!/usr/bin/env python
    \"\"\"Django's command-line utility for administrative tasks.\"\"\"
    import os
    import sys


    def main():
        \"\"\"Run administrative tasks.\"\"\"
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personnel_accounting.settings.development')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(sys.argv)


    if __name__ == '__main__':
        main()
    """,
    "requirements.txt": """
    Django>=5.0
    psycopg2-binary
    python-decouple
    django-mptt
    django-crispy-forms
    crispy-tailwind
    django-extensions
    Pillow>=10.0
    """,
    ".gitignore": """
    # Python
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
    .Python
    build/
    develop-eggs/
    dist/
    downloads/
    eggs/
    .eggs/
    lib/
    lib64/
    parts/
    sdist/
    var/
    wheels/
    *.egg-info/
    .installed.cfg
    *.egg
    MANIFEST

    # Virtualenv
    .env
    venv/
    env/
    .venv/

    # Docker
    .dockerignore
    docker-compose.yml.local
    .postgres_data/

    # Django
    *.log
    local_settings.py
    db.sqlite3
    db.sqlite3-journal
    media/
    static_root/
    staticfiles/

    # IDE
    .idea/
    .vscode/
    *.swp
    """,
    ".env.example": """
    # Django settings
    SECRET_KEY=your-super-secret-key-goes-here
    DEBUG=True

    # Database settings (for Docker container and local Django)
    DB_NAME=personnel_db
    DB_USER=personnel_user
    DB_PASSWORD=strongpassword
    DB_HOST=127.0.0.1
    DB_PORT=5432
    """,
    "docker-compose.yml": """
    version: '3.8'

    services:
      db:
        image: postgres:17-alpine
        container_name: asoos_postgres_db
        restart: always
        volumes:
          - ./.postgres_data:/var/lib/postgresql/data/
        environment:
          POSTGRES_DB: ${DB_NAME}
          POSTGRES_USER: ${DB_USER}
          POSTGRES_PASSWORD: ${DB_PASSWORD}
        ports:
          - "${DB_PORT}:5432"
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
          interval: 5s
          timeout: 5s
          retries: 5
    """,
    "Makefile": """
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
    """,

    # --- Основний конфігураційний пакет проєкту ---
    f"{PROJECT_NAME}/__init__.py": "",
    f"{PROJECT_NAME}/asgi.py": """
    import os
    from django.core.asgi import get_asgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personnel_accounting.settings.development')
    application = get_asgi_application()
    """,
    f"{PROJECT_NAME}/wsgi.py": """
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personnel_accounting.settings.development')
    application = get_wsgi_application()
    """,
    f"{PROJECT_NAME}/urls.py": """
    from django.contrib import admin
    from django.urls import path, include
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('apps.personnel.urls')),
        path('staffing/', include('apps.staffing.urls')),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """,

    # --- Налаштування проєкту ---
    f"{PROJECT_NAME}/settings/__init__.py": "",
    f"{PROJECT_NAME}/settings/base.py": """
    from pathlib import Path
    from decouple import config

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    SECRET_KEY = config('SECRET_KEY')
    DEBUG = config('DEBUG', default=False, cast=bool)

    ALLOWED_HOSTS = []

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third-party apps
        'mptt',
        'crispy_forms',
        'crispy_tailwind',
        'django_extensions',

        # Local apps
        'apps.core.apps.CoreConfig',
        'apps.users.apps.UsersConfig',
        'apps.staffing.apps.StaffingConfig',
        'apps.personnel.apps.PersonnelConfig',
        'apps.reporting.apps.ReportingConfig',
        'apps.auditing.apps.AuditingConfig',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'personnel_accounting.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'personnel_accounting.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/5.0/ref/settings/#databases
    # Налаштування бази даних буде в development.py / production.py

    AUTH_USER_MODEL = 'users.User'

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]

    LANGUAGE_CODE = 'uk-ua'
    TIME_ZONE = 'Europe/Kyiv'
    USE_I18N = True
    USE_TZ = True

    STATIC_URL = 'static/'
    STATICFILES_DIRS = [BASE_DIR / 'static']
    STATIC_ROOT = BASE_DIR / 'staticfiles'

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
    CRISPY_TEMPLATE_PACK = "tailwind"
    """,
    f"{PROJECT_NAME}/settings/development.py": """
    from .base import *
    from decouple import config

    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='127.0.0.1'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
    """,

    # --- Додаток 'core' ---
    f"{APPS_DIR}/core/apps.py": """
    from django.apps import AppConfig

    class CoreConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.core'
        verbose_name = 'Основні компоненти'
    """,

    # --- Додаток 'users' ---
    f"{APPS_DIR}/users/apps.py": """
    from django.apps import AppConfig

    class UsersConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.users'
        verbose_name = 'Користувачі та Профілі'
    """,
    f"{APPS_DIR}/users/models.py": """
    from django.contrib.auth.models import AbstractUser
    from django.db import models

    class User(AbstractUser):
        middle_name = models.CharField("По батькові", max_length=150, blank=True)

        def get_full_name(self):
            full_name = '%s %s %s' % (self.last_name, self.first_name, self.middle_name)
            return full_name.strip()

        def __str__(self):
            return self.username
    """,
    f"{APPS_DIR}/users/admin.py": """
    from django.contrib import admin
    from django.contrib.auth.admin import UserAdmin
    from .models import User

    @admin.register(User)
    class CustomUserAdmin(UserAdmin):
        model = User
        fieldsets = UserAdmin.fieldsets + (
            ('Додаткова інформація', {'fields': ('middle_name',)}),
        )
        list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    """,

    # --- Додаток 'staffing' ---
    f"{APPS_DIR}/staffing/apps.py": """
    from django.apps import AppConfig

    class StaffingConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.staffing'
        verbose_name = 'Штатно-посадовий облік'
    """,
    f"{APPS_DIR}/staffing/models.py": """
    from django.db import models
    from mptt.models import MPTTModel, TreeForeignKey

    class Unit(MPTTModel):
        \"\"\"Підрозділ (військова частина, батальйон, рота тощо)\"\"\"
        name = models.CharField("Найменування підрозділу", max_length=255)
        parent = TreeForeignKey(
            'self',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='children',
            db_index=True,
            verbose_name="Вищий підрозділ"
        )

        class MPTTMeta:
            order_insertion_by = ['name']

        class Meta:
            verbose_name = "Підрозділ"
            verbose_name_plural = "Підрозділи"

        def __str__(self):
            return self.name

    class MilitarySpecialty(models.Model):
        \"\"\"Військово-облікова спеціальність (ВОС) - довідник\"\"\"
        code = models.CharField("Код ВОС", max_length=20, unique=True)
        name = models.CharField("Найменування", max_length=255)

        class Meta:
            verbose_name = "Військово-облікова спеціальність"
            verbose_name_plural = "Військово-облікові спеціальності"

        def __str__(self):
            return f"{self.code} - {self.name}"

    class Position(models.Model):
        \"\"\"Посада згідно зі штатом\"\"\"
        unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Підрозділ", related_name="positions")
        position_index = models.CharField("Індекс посади", max_length=50, unique=True)
        name = models.CharField("Найменування посади", max_length=255)
        category = models.CharField("Штатно-посадова категорія", max_length=100)
        specialty = models.ForeignKey(MilitarySpecialty, on_delete=models.PROTECT, verbose_name="Військово-облікова спеціальність")
        tariff_rate = models.CharField("Тарифний розряд", max_length=50)

        class Meta:
            verbose_name = "Посада"
            verbose_name_plural = "Посади"
            ordering = ['name']

        def __str__(self):
            return f"{self.name} ({self.unit.name})"
    """,
    f"{APPS_DIR}/staffing/admin.py": """
    from django.contrib import admin
    from mptt.admin import DraggableMPTTAdmin
    from .models import Unit, MilitarySpecialty, Position

    @admin.register(Unit)
    class UnitAdmin(DraggableMPTTAdmin):
        list_display = ('tree_actions', 'indented_title')
        list_display_links = ('indented_title',)
        search_fields = ('name',)

    @admin.register(MilitarySpecialty)
    class MilitarySpecialtyAdmin(admin.ModelAdmin):
        list_display = ('code', 'name')
        search_fields = ('code', 'name')

    @admin.register(Position)
    class PositionAdmin(admin.ModelAdmin):
        list_display = ('name', 'unit', 'position_index', 'category', 'specialty')
        list_filter = ('unit', 'specialty', 'category')
        search_fields = ('name', 'position_index', 'unit__name')
        autocomplete_fields = ('unit', 'specialty')
    """,
    f"{APPS_DIR}/staffing/views.py": """
    from django.views.generic import ListView, DetailView
    from .models import Unit

    class UnitListView(ListView):
        model = Unit
        template_name = 'staffing/unit_list.html'
        context_object_name = 'units'

    class UnitDetailView(DetailView):
        model = Unit
        template_name = 'staffing/unit_detail.html'
        context_object_name = 'unit'
    """,
    f"{APPS_DIR}/staffing/urls.py": """
    from django.urls import path
    from .views import UnitListView, UnitDetailView

    app_name = 'staffing'

    urlpatterns = [
        path('', UnitListView.as_view(), name='unit-list'),
        path('<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),
    ]
    """,

    # --- Додаток 'personnel' ---
    f"{APPS_DIR}/personnel/apps.py": """
    from django.apps import AppConfig

    class PersonnelConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.personnel'
        verbose_name = 'Персональний облік'
    """,
    f"{APPS_DIR}/personnel/models.py": """
    from django.db import models
    from django.conf import settings

    class Rank(models.Model):
        \"\"\"Військове звання - довідник\"\"\"
        name = models.CharField("Назва звання", max_length=100, unique=True)
        order = models.PositiveIntegerField("Порядок сортування", default=0)

        class Meta:
            verbose_name = "Військове звання"
            verbose_name_plural = "Військові звання"
            ordering = ['order']

        def __str__(self):
            return self.name

    class Serviceman(models.Model):
        \"\"\"Військовослужбовець - центральна модель персонального обліку\"\"\"
        user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name="Обліковий запис"
        )
        position = models.OneToOneField(
            'staffing.Position',
            on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name="Посада"
        )

        # Персональні дані згідно з Наказом № 687
        rank = models.ForeignKey(Rank, on_delete=models.PROTECT, verbose_name="Військове звання")
        last_name = models.CharField("Прізвище", max_length=100)
        first_name = models.CharField("Ім'я", max_length=100)
        middle_name = models.CharField("По батькові", max_length=100, blank=True)

        date_of_birth = models.DateField("Дата народження")
        place_of_birth = models.CharField("Місце народження", max_length=255)
        tax_id_number = models.CharField("РНОКПП", max_length=10, unique=True, null=True, blank=True)
        passport_number = models.CharField("Номер документа, що посвідчує особу", max_length=50)

        photo = models.ImageField("Фото", upload_to='servicemen_photos/', null=True, blank=True)

        class Meta:
            verbose_name = "Військовослужбовець"
            verbose_name_plural = "Військовослужбовці"
            ordering = ['last_name', 'first_name']

        def __str__(self):
            return f"{self.rank} {self.last_name} {self.first_name}"

        @property
        def full_name(self):
            return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    class Contract(models.Model):
        \"\"\"Контракт військовослужбовця\"\"\"
        serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='contracts')
        start_date = models.DateField("Дата укладення контракту")
        end_date = models.DateField("Дата закінчення контракту")
        details = models.TextField("Деталі контракту", blank=True)

        class Meta:
            verbose_name = "Контракт"
            verbose_name_plural = "Контракти"
            ordering = ['-start_date']

    class ServiceHistoryEvent(models.Model):
        \"\"\"Журнал подій в історії служби\"\"\"
        class EventType(models.TextChoices):
            APPOINTMENT = 'APPOINTMENT', 'Призначення'
            TRANSFER = 'TRANSFER', 'Переведення'
            PROMOTION = 'PROMOTION', 'Підвищення у званні'
            DISMISSAL = 'DISMISSAL', 'Звільнення'

        serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='service_history')
        event_type = models.CharField("Тип події", max_length=20, choices=EventType.choices)
        event_date = models.DateField("Дата події")
        details = models.JSONField("Деталі", default=dict, help_text="Зберігає деталі, напр. new_rank, new_position")
        order_reference = models.CharField("Посилання на наказ", max_length=255)

        class Meta:
            verbose_name = "Подія в історії служби"
            verbose_name_plural = "Історія служби"
            ordering = ['-event_date']
    """,
    f"{APPS_DIR}/personnel/admin.py": """
    from django.contrib import admin
    from .models import Rank, Serviceman, Contract, ServiceHistoryEvent

    @admin.register(Rank)
    class RankAdmin(admin.ModelAdmin):
        list_display = ('name', 'order')
        list_editable = ('order',)

    class ContractInline(admin.TabularInline):
        model = Contract
        extra = 1

    class ServiceHistoryEventInline(admin.TabularInline):
        model = ServiceHistoryEvent
        extra = 1
        readonly_fields = ('details', 'order_reference', 'event_type', 'event_date')

    @admin.register(Serviceman)
    class ServicemanAdmin(admin.ModelAdmin):
        list_display = ('full_name', 'rank', 'position')
        list_filter = ('rank', 'position__unit')
        search_fields = ('last_name', 'first_name', 'tax_id_number')
        autocomplete_fields = ('position', 'user')
        inlines = [ContractInline, ServiceHistoryEventInline]
        readonly_fields = ('user',)
    """,
    f"{APPS_DIR}/personnel/views.py": """
    from django.views.generic import ListView, DetailView
    from .models import Serviceman

    class ServicemanListView(ListView):
        model = Serviceman
        template_name = 'personnel/serviceman_list.html'
        context_object_name = 'servicemen'
        paginate_by = 20

    class ServicemanDetailView(DetailView):
        model = Serviceman
        template_name = 'personnel/serviceman_detail.html'
        context_object_name = 'serviceman'
    """,
    f"{APPS_DIR}/personnel/urls.py": """
    from django.urls import path
    from .views import ServicemanListView, ServicemanDetailView

    app_name = 'personnel'

    urlpatterns = [
        path('', ServicemanListView.as_view(), name='serviceman-list'),
        path('serviceman/<int:pk>/', ServicemanDetailView.as_view(), name='serviceman-detail'),
    ]
    """,
    f"{APPS_DIR}/personnel/services.py": """
    from django.db import transaction
    from .models import Serviceman, ServiceHistoryEvent
    from apps.staffing.models import Position
    from datetime import date

    @transaction.atomic
    def transfer_serviceman(serviceman: Serviceman, new_position: Position, order_reference: str, event_date: date):
        \"\"\"
        Виконує повний процес переведення військовослужбовця на нову посаду.
        Ця функція є прикладом реалізації бізнес-логіки в сервісному шарі.
        \"\"\"
        old_position = serviceman.position

        # Перевіряємо, чи нова посада не зайнята
        if hasattr(new_position, 'serviceman') and new_position.serviceman is not None:
             raise ValueError(f"Посада {new_position} вже зайнята.")

        # Призначаємо нову посаду
        serviceman.position = new_position
        serviceman.save()

        # Створюємо запис в історії служби
        ServiceHistoryEvent.objects.create(
            serviceman=serviceman,
            event_type=ServiceHistoryEvent.EventType.TRANSFER,
            event_date=event_date,
            details={
                'from_position_id': old_position.id if old_position else None,
                'from_position_name': str(old_position) if old_position else 'N/A',
                'to_position_id': new_position.id,
                'to_position_name': str(new_position),
            },
            order_reference=order_reference
        )

        # Тут може бути додаткова логіка, напр. відправка сповіщень
        print(f"Військовослужбовця {serviceman} переведено на посаду {new_position}.")

        return serviceman
    """,

    # --- Додаток 'reporting' ---
    f"{APPS_DIR}/reporting/apps.py": """
    from django.apps import AppConfig

    class ReportingConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.reporting'
        verbose_name = 'Звітність та Статистика'
    """,

    # --- Додаток 'auditing' ---
    f"{APPS_DIR}/auditing/apps.py": """
    from django.apps import AppConfig

    class AuditingConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'apps.auditing'
        verbose_name = 'Аудит та Журналювання'
    """,

    # --- Шаблони (Templates) ---
    "templates/base.html": """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}АСООС 'ОБРІГ'{% endblock %}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 font-sans">
        <nav class="bg-gray-800 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <a href="{% url 'personnel:serviceman-list' %}" class="text-xl font-bold">АСООС 'ОБРІГ'</a>
                <div>
                    <a href="{% url 'personnel:serviceman-list' %}" class="px-3 py-2 rounded hover:bg-gray-700">Особовий склад</a>
                    <a href="{% url 'staffing:unit-list' %}" class="px-3 py-2 rounded hover:bg-gray-700">Підрозділи</a>
                    <a href="/admin/" class="px-3 py-2 rounded hover:bg-gray-700">Адмін-панель</a>
                </div>
            </div>
        </nav>

        <main class="container mx-auto mt-8 p-4">
            {% block content %}
            {% endblock %}
        </main>

        <footer class="bg-gray-800 text-white text-center p-4 mt-8">
            <p>&copy; 2025 Міністерство Оборони України. Всі права захищено.</p>
        </footer>
    </body>
    </html>
    """,
    "templates/personnel/serviceman_list.html": """
    {% extends "base.html" %}

    {% block title %}Список особового складу - АСООС 'ОБРІГ'{% endblock %}

    {% block content %}
    <div class="bg-white p-6 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-gray-800">Список особового складу</h1>

        <div class="overflow-x-auto">
            <table class="min-w-full bg-white">
                <thead class="bg-gray-800 text-white">
                    <tr>
                        <th class="py-3 px-4 uppercase font-semibold text-sm text-left">ПІБ</th>
                        <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Звання</th>
                        <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Посада</th>
                        <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Підрозділ</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    {% for serviceman in servicemen %}
                    <tr class="hover:bg-gray-100 border-b">
                        <td class="py-3 px-4">
                            <a href="{% url 'personnel:serviceman-detail' serviceman.pk %}" class="text-blue-600 hover:underline">
                                {{ serviceman.full_name }}
                            </a>
                        </td>
                        <td class="py-3 px-4">{{ serviceman.rank }}</td>
                        <td class="py-3 px-4">{{ serviceman.position.name|default:"Не призначено" }}</td>
                        <td class="py-3 px-4">{{ serviceman.position.unit.name|default:"N/A" }}</td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="4" class="text-center py-4">Немає даних про особовий склад.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    """,
    "templates/personnel/serviceman_detail.html": """
    {% extends "base.html" %}

    {% block title %}{{ serviceman.full_name }} - АСООС 'ОБРІГ'{% endblock %}

    {% block content %}
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-4xl mx-auto">
        <div class="flex items-center space-x-6 mb-6">
            <div class="w-32 h-32 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                {% if serviceman.photo %}
                    <img src="{{ serviceman.photo.url }}" alt="Фото" class="w-full h-full object-cover">
                {% else %}
                    <span class="text-gray-500">Фото</span>
                {% endif %}
            </div>
            <div>
                <h1 class="text-4xl font-bold text-gray-800">{{ serviceman.full_name }}</h1>
                <p class="text-2xl text-gray-600">{{ serviceman.rank }}</p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-gray-50 p-4 rounded-md">
                <h2 class="text-xl font-semibold mb-2 text-gray-700">Основна інформація</h2>
                <p><strong>Посада:</strong> {{ serviceman.position.name|default:"Не призначено" }}</p>
                <p><strong>Підрозділ:</strong> {{ serviceman.position.unit.name|default:"N/A" }}</p>
                <p><strong>Дата народження:</strong> {{ serviceman.date_of_birth|date:"d.m.Y" }}</p>
                <p><strong>Місце народження:</strong> {{ serviceman.place_of_birth }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-md">
                <h2 class="text-xl font-semibold mb-2 text-gray-700">Ідентифікаційні дані</h2>
                <p><strong>РНОКПП:</strong> {{ serviceman.tax_id_number|default:"Не вказано" }}</p>
                <p><strong>Паспорт:</strong> {{ serviceman.passport_number|default:"Не вказано" }}</p>
            </div>
        </div>

        <div class="mt-8">
            <h2 class="text-2xl font-semibold mb-4 text-gray-700">Історія служби</h2>
            <ul class="space-y-2">
                {% for event in serviceman.service_history.all %}
                <li class="bg-gray-100 p-3 rounded-md">
                    <p class="font-semibold">{{ event.get_event_type_display }} - {{ event.event_date|date:"d.m.Y" }}</p>
                    <p class="text-sm text-gray-600">Наказ: {{ event.order_reference }}</p>
                </li>
                {% empty %}
                <p>Немає записів в історії служби.</p>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% endblock %}
    """,
    "templates/staffing/unit_list.html": """
    {% extends "base.html" %}
    {% load mptt_tags %}

    {% block title %}Структура підрозділів - АСООС 'ОБРІГ'{% endblock %}

    {% block content %}
    <div class="bg-white p-6 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-gray-800">Структура підрозділів</h1>

        <ul class="list-none p-0">
            {% recursetree units %}
                <li class="p-2 rounded {% if not node.is_leaf_node %}mb-2{% endif %}">
                    <a href="{% url 'staffing:unit-detail' node.pk %}" class="text-blue-600 hover:underline font-semibold">
                        {{ node.name }}
                    </a>
                    {% if not node.is_leaf_node %}
                        <ul class="list-none pl-6 mt-2 border-l-2 border-gray-200">
                            {{ children }}
                        </ul>
                    {% endif %}
                </li>
            {% endrecursetree %}
        </ul>
    </div>
    {% endblock %}
    """,
    "templates/staffing/unit_detail.html": """
    {% extends "base.html" %}

    {% block title %}{{ unit.name }} - АСООС 'ОБРІГ'{% endblock %}

    {% block content %}
    <div class="bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-2 text-gray-800">{{ unit.name }}</h1>
        {% if unit.parent %}
        <p class="text-lg text-gray-600 mb-6">Входить до складу: <a href="{% url 'staffing:unit-detail' unit.parent.pk %}" class="text-blue-600 hover:underline">{{ unit.parent.name }}</a></p>
        {% endif %}

        <div class="mt-8">
            <h2 class="text-2xl font-semibold mb-4 text-gray-700">Штатні посади</h2>
            <div class="space-y-2">
                {% for position in unit.positions.all %}
                    <div class="bg-gray-50 p-3 rounded-md">
                        <p class="font-semibold">{{ position.name }}</p>
                        <p class="text-sm text-gray-600">Індекс: {{ position.position_index }} | ВОС: {{ position.specialty.code }}</p>
                    </div>
                {% empty %}
                    <p>У цьому підрозділі немає штатних посад.</p>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endblock %}
    """,
}


# ==============================================================================
# ЛОГІКА ГЕНЕРАТОРА
# Цей код створює папки та файли на основі конфігурації вище.
# ==============================================================================

def create_project_structure():
    """Створює структуру папок та файлів проєкту."""
    print("🚀 Починаю створення проєкту АСООС 'ОБРІГ'...")

    # Створення кореневих папок
    base_dirs = [PROJECT_NAME, APPS_DIR, "templates", "static", "media"]
    for directory in base_dirs:
        os.makedirs(directory, exist_ok=True)

    # Створення папок для додатків та базових файлів
    for app_name in APP_NAMES:
        app_path = os.path.join(APPS_DIR, app_name)
        os.makedirs(app_path, exist_ok=True)
        # Створюємо пусті файли __init__.py, якщо вони не визначені
        if not os.path.exists(os.path.join(app_path, "__init__.py")):
            open(os.path.join(app_path, "__init__.py"), 'a').close()
        # Створюємо пусті файли, які можуть знадобитися, але не заповнені
        for empty_file in ["models.py", "admin.py", "views.py", "urls.py", "services.py"]:
            full_path = os.path.join(app_path, empty_file)
            if full_path not in project_files and not os.path.exists(full_path):
                open(full_path, 'a').close()

    # Створення всіх файлів з їхнім вмістом
    for file_path, content in project_files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(content).strip())
        print(f"✅ Створено файл: {file_path}")

    # Створення додаткових папок для шаблонів
    os.makedirs("templates/personnel", exist_ok=True)
    os.makedirs("templates/staffing", exist_ok=True)

    print("\n🎉 Структуру проєкту успішно створено!")
    print("=" * 60)
    print("✅ ВИПРАВЛЕНИЙ ПОРЯДОК ЗАПУСКУ (з Docker та Make):")
    print("\n0.  Переконайтесь, що у вас встановлено Docker та Docker Compose.")
    print("    Якщо виникали помилки, почніть з чистого аркуша: make fresh-start")
    print("\n1.  Створіть та активуйте віртуальне середовище Python:")
    print("    python -m venv venv")
    print("    source venv/bin/activate  # для Linux/macOS")
    print("    .\\venv\\Scripts\\activate    # для Windows")
    print("\n2.  Налаштуйте файл .env:")
    print("    - Скопіюйте .env.example в .env.")
    print("    - Відредагуйте .env, вказавши надійний SECRET_KEY.")
    print("\n3.  Запустіть базу даних в Docker:")
    print("    make up")
    print("\n4.  Встановіть залежності Python:")
    print("    make install")
    print("\n5.  ‼️ ВАЖЛИВО: Створіть файли міграцій:")
    print("    make makemigrations")
    print("\n6.  Тепер застосуйте міграції та створіть адміністратора:")
    print("    make migrate")
    print("    make superuser")
    print("\n7.  Запустіть локальний сервер Django:")
    print("    make run")
    print("\n8.  Відкрийте проєкт у вашому браузері:")
    print("    - Основна сторінка: http://127.0.0.1:8000/")
    print("    - Адмін-панель: http://127.0.0.1:8000/admin/")
    print("\n💡 Для перегляду всіх доступних команд, виконайте: make help")
    print("=" * 60)


if __name__ == "__main__":
    create_project_structure()
