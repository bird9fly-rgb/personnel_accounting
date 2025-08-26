# apps/users/permissions.py
"""
Модуль для управління правами доступу та групами користувачів
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.personnel.models import Serviceman, Contract, ServiceHistoryEvent
from apps.staffing.models import Unit, Position, MilitarySpecialty
from apps.users.models import User


class PermissionManager:
    """Менеджер для управління правами доступу в системі"""

    GROUPS = {
        'Адміністратори системи': {
            'description': 'Повний доступ до всіх функцій системи',
            'permissions': 'all'
        },
        'Кадрові офіцери': {
            'description': 'Управління особовим складом та контрактами',
            'permissions': [
                # Персонал
                'personnel.add_serviceman',
                'personnel.change_serviceman',
                'personnel.delete_serviceman',
                'personnel.view_serviceman',
                'personnel.can_promote',
                'personnel.can_transfer',
                # Контракти
                'personnel.add_contract',
                'personnel.change_contract',
                'personnel.delete_contract',
                'personnel.view_contract',
                # Історія служби
                'personnel.add_servicehistoryevent',
                'personnel.change_servicehistoryevent',
                'personnel.view_servicehistoryevent',
                # Звання
                'personnel.view_rank',
                # Посади
                'staffing.view_position',
                'staffing.change_position',
                # Підрозділи
                'staffing.view_unit',
            ]
        },
        'Командири підрозділів': {
            'description': 'Перегляд підлеглого особового складу',
            'permissions': [
                'personnel.view_serviceman',
                'personnel.view_contract',
                'personnel.view_servicehistoryevent',
                'personnel.view_rank',
                'staffing.view_position',
                'staffing.view_unit',
                'staffing.view_militaryspecialty',
            ]
        },
        'Штабні офіцери': {
            'description': 'Робота зі звітністю та аналітикою',
            'permissions': [
                'personnel.view_serviceman',
                'personnel.view_contract',
                'personnel.view_servicehistoryevent',
                'personnel.view_rank',
                'staffing.view_position',
                'staffing.view_unit',
                'staffing.view_militaryspecialty',
                'reporting.view_report',
                'reporting.create_report',
            ]
        },
        'Медичні працівники': {
            'description': 'Доступ до медичних даних особового складу',
            'permissions': [
                'personnel.view_serviceman',
                'personnel.view_medical_data',
                'personnel.change_medical_data',
            ]
        },
        'Фінансові офіцери': {
            'description': 'Робота з фінансовими даними',
            'permissions': [
                'personnel.view_serviceman',
                'personnel.view_contract',
                'personnel.view_financial_data',
                'personnel.change_financial_data',
            ]
        },
        'Оператори': {
            'description': 'Базовий перегляд даних',
            'permissions': [
                'personnel.view_serviceman',
                'personnel.view_rank',
                'staffing.view_position',
                'staffing.view_unit',
            ]
        }
    }

    @classmethod
    @transaction.atomic
    def setup_groups(cls):
        """Створення груп користувачів з відповідними правами"""
        created_groups = []

        for group_name, config in cls.GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                created_groups.append(group_name)

            # Очищаємо існуючі права для оновлення
            group.permissions.clear()

            if config['permissions'] == 'all':
                # Надаємо всі права для адміністраторів
                permissions = Permission.objects.all()
                group.permissions.set(permissions)
            else:
                # Надаємо специфічні права
                for perm_string in config['permissions']:
                    try:
                        app_label, codename = perm_string.split('.')
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )
                        group.permissions.add(permission)
                    except (Permission.DoesNotExist, ValueError):
                        print(f"Попередження: Право {perm_string} не знайдено")

            print(f"✅ Група '{group_name}' налаштована")

        return created_groups

    @classmethod
    def assign_user_to_group(cls, user, group_name):
        """Призначення користувача до групи"""
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            print(f"✅ Користувач {user.username} доданий до групи '{group_name}'")
            return True
        except Group.DoesNotExist:
            print(f"❌ Група '{group_name}' не існує")
            return False

    @classmethod
    def remove_user_from_group(cls, user, group_name):
        """Видалення користувача з групи"""
        try:
            group = Group.objects.get(name=group_name)
            user.groups.remove(group)
            print(f"✅ Користувач {user.username} видалений з групи '{group_name}'")
            return True
        except Group.DoesNotExist:
            print(f"❌ Група '{group_name}' не існує")
            return False

    @classmethod
    def get_user_permissions(cls, user):
        """Отримання всіх прав користувача"""
        if user.is_superuser:
            return Permission.objects.all()

        return user.user_permissions.all() | Permission.objects.filter(group__user=user)

    @classmethod
    def user_has_permission(cls, user, permission_string):
        """Перевірка чи має користувач певне право"""
        if user.is_superuser:
            return True

        return user.has_perm(permission_string)

    @classmethod
    def get_users_in_group(cls, group_name):
        """Отримання всіх користувачів в групі"""
        try:
            group = Group.objects.get(name=group_name)
            return group.user_set.all()
        except Group.DoesNotExist:
            return User.objects.none()

    @classmethod
    def create_custom_permissions(cls):
        """Створення додаткових прав, які не створюються автоматично Django"""
        custom_permissions = [
            {
                'app_label': 'personnel',
                'model': 'serviceman',
                'permissions': [
                    ('can_promote', 'Може підвищувати у званні'),
                    ('can_transfer', 'Може переводити на інші посади'),
                    ('view_medical_data', 'Може переглядати медичні дані'),
                    ('change_medical_data', 'Може змінювати медичні дані'),
                    ('view_financial_data', 'Може переглядати фінансові дані'),
                    ('change_financial_data', 'Може змінювати фінансові дані'),
                ]
            },
            {
                'app_label': 'reporting',
                'model': 'report',
                'permissions': [
                    ('view_report', 'Може переглядати звіти'),
                    ('create_report', 'Може створювати звіти'),
                    ('export_report', 'Може експортувати звіти'),
                ]
            },
            {
                'app_label': 'auditing',
                'model': 'auditlog',
                'permissions': [
                    ('view_audit_log', 'Може переглядати журнал аудиту'),
                    ('export_audit_log', 'Може експортувати журнал аудиту'),
                ]
            }
        ]

        for config in custom_permissions:
            try:
                content_type = ContentType.objects.get(
                    app_label=config['app_label'],
                    model=config['model']
                )

                for codename, name in config['permissions']:
                    Permission.objects.get_or_create(
                        codename=codename,
                        name=name,
                        content_type=content_type
                    )
                    print(f"✅ Створено право: {config['app_label']}.{codename}")

            except ContentType.DoesNotExist:
                print(f"❌ Модель {config['app_label']}.{config['model']} не знайдена")

    @classmethod
    def setup_test_users_permissions(cls):
        """Налаштування прав для тестових користувачів"""
        assignments = [
            ('admin', 'Адміністратори системи'),
            ('hr_officer', 'Кадрові офіцери'),
            ('commander', 'Командири підрозділів'),
        ]

        for username, group_name in assignments:
            try:
                user = User.objects.get(username=username)
                cls.assign_user_to_group(user, group_name)
            except User.DoesNotExist:
                print(f"❌ Користувач {username} не існує")


# Декоратори для views
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def permission_required_with_message(permission, message="У вас немає прав для виконання цієї дії"):
    """Декоратор для перевірки прав з кастомним повідомленням"""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                raise PermissionDenied(message)
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def group_required(group_name):
    """Декоратор для перевірки належності до групи"""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                raise PermissionDenied(f"Доступ дозволено тільки для групи '{group_name}'")
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def unit_commander_required(view_func):
    """Декоратор для перевірки чи є користувач командиром підрозділу"""

    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'serviceman'):
            raise PermissionDenied("Тільки військовослужбовці мають доступ до цієї функції")

        serviceman = request.user.serviceman
        if not serviceman.position or 'Командир' not in serviceman.position.name:
            raise PermissionDenied("Доступ дозволено тільки командирам підрозділів")

        return view_func(request, *args, **kwargs)

    return wrapped_view