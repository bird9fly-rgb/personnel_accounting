# apps/auditing/mixins.py
"""
Міксини для автоматичного логування змін в моделях
"""

from django.db import models
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from .models import AuditLog
import json


class AuditMixin(models.Model):
    """
    Міксин для автоматичного логування змін в моделях.
    Додайте цей міксин до будь-якої моделі для автоматичного відстеження змін.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Перевизначений метод save з логуванням"""
        # Визначаємо чи це нова модель
        is_new = self.pk is None
        old_values = {}

        # Отримуємо старі значення якщо це оновлення
        if not is_new:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                old_values = model_to_dict(old_instance)
            except self.__class__.DoesNotExist:
                is_new = True

        # Зберігаємо об'єкт
        super().save(*args, **kwargs)

        # Отримуємо нові значення
        new_values = model_to_dict(self)

        # Визначаємо користувача (якщо можливо)
        user = self._get_current_user()

        # Логуємо зміни
        if is_new:
            AuditLog.log_action(
                user=user,
                action='CREATE',
                obj=self,
                changes={'new': self._serialize_values(new_values)}
            )
        else:
            # Визначаємо що змінилось
            changes = self._get_changes(old_values, new_values)
            if changes:
                AuditLog.log_action(
                    user=user,
                    action='UPDATE',
                    obj=self,
                    changes=changes
                )

    def delete(self, *args, **kwargs):
        """Перевизначений метод delete з логуванням"""
        # Зберігаємо дані перед видаленням
        deleted_data = model_to_dict(self)

        # Отримуємо користувача
        user = self._get_current_user()

        # Логуємо видалення
        AuditLog.log_action(
            user=user,
            action='DELETE',
            obj=self,
            changes={'deleted': self._serialize_values(deleted_data)}
        )

        # Видаляємо об'єкт
        super().delete(*args, **kwargs)

    def _get_current_user(self):
        """Спроба отримати поточного користувача"""
        # Це можна реалізувати через middleware або thread locals
        # Для простоти повертаємо None
        return None

    def _serialize_values(self, values):
        """Серіалізація значень для збереження в JSON"""
        serialized = {}
        for key, value in values.items():
            if isinstance(value, models.Model):
                serialized[key] = str(value)
            elif hasattr(value, 'isoformat'):
                serialized[key] = value.isoformat()
            else:
                try:
                    json.dumps(value)
                    serialized[key] = value
                except (TypeError, ValueError):
                    serialized[key] = str(value)
        return serialized

    def _get_changes(self, old_values, new_values):
        """Визначення змінених полів"""
        changes = {'old': {}, 'new': {}}

        for field, new_value in new_values.items():
            old_value = old_values.get(field)

            # Порівнюємо значення
            if old_value != new_value:
                changes['old'][field] = self._serialize_value(old_value)
                changes['new'][field] = self._serialize_value(new_value)

        return changes if changes['old'] else None

    def _serialize_value(self, value):
        """Серіалізація одного значення"""
        if isinstance(value, models.Model):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        else:
            try:
                json.dumps(value)
                return value
            except (TypeError, ValueError):
                return str(value)


class ViewAuditMixin:
    """Міксин для логування переглядів у Django views"""

    def get(self, request, *args, **kwargs):
        """Логування GET запитів"""
        response = super().get(request, *args, **kwargs)

        # Логуємо перегляд
        if hasattr(self, 'get_object'):
            try:
                obj = self.get_object()
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action='VIEW',
                    obj=obj,
                    request=request
                )
            except:
                pass

        return response


class BulkOperationMixin:
    """Міксин для логування масових операцій"""

    def perform_bulk_action(self, queryset, action_name, user=None):
        """Виконання масової операції з логуванням"""
        affected_objects = list(queryset)

        # Логуємо масову операцію
        AuditLog.log_action(
            user=user,
            action='UPDATE',
            changes={
                'bulk_action': action_name,
                'affected_count': len(affected_objects),
                'affected_ids': [obj.pk for obj in affected_objects]
            },
            severity='WARNING',
            notes=f"Масова операція: {action_name}"
        )

        return affected_objects


class SensitiveDataMixin(models.Model):
    """Міксин для моделей з чутливими даними"""

    class Meta:
        abstract = True

    # Поля, які вважаються чутливими
    SENSITIVE_FIELDS = []

    def save(self, *args, **kwargs):
        """Додаткове логування для чутливих даних"""
        is_new = self.pk is None

        # Перевіряємо зміни в чутливих полях
        if not is_new:
            old_instance = self.__class__.objects.get(pk=self.pk)
            for field in self.SENSITIVE_FIELDS:
                old_value = getattr(old_instance, field, None)
                new_value = getattr(self, field, None)

                if old_value != new_value:
            # Логуємо з