# apps/users/management/commands/setup_permissions.py
"""
Management command для налаштування груп та прав доступу
Використання: python manage.py setup_permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.permissions import PermissionManager

User = get_user_model()


class Command(BaseCommand):
    help = 'Налаштовує групи користувачів та права доступу в системі'

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-test-users',
            action='store_true',
            help='Призначити права тестовим користувачам'
        )
        parser.add_argument(
            '--create-custom-permissions',
            action='store_true',
            help='Створити кастомні права доступу'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔐 Налаштування системи прав доступу...\n')

        # Створюємо кастомні права якщо потрібно
        if options.get('create_custom_permissions'):
            self.stdout.write('📝 Створення кастомних прав...')
            PermissionManager.create_custom_permissions()

        # Створюємо групи з правами
        self.stdout.write('👥 Створення груп користувачів...')
        created_groups = PermissionManager.setup_groups()

        if created_groups:
            self.stdout.write(self.style.SUCCESS(f'✅ Створено {len(created_groups)} нових груп'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️ Всі групи вже існують'))

        # Призначаємо права тестовим користувачам
        if options.get('assign_test_users'):
            self.stdout.write('\n👤 Призначення прав тестовим користувачам...')
            PermissionManager.setup_test_users_permissions()

        # Виводимо статистику
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('📊 СТАТИСТИКА ПРАВ ДОСТУПУ:')
        self.stdout.write('=' * 50)

        for group_name, config in PermissionManager.GROUPS.items():
            users_count = PermissionManager.get_users_in_group(group_name).count()
            self.stdout.write(f'\n📁 {group_name}:')
            self.stdout.write(f'   Опис: {config["description"]}')
            self.stdout.write(f'   Користувачів: {users_count}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Налаштування прав доступу завершено!'))