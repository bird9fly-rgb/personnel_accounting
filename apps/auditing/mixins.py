# apps/auditing/mixins.py
"""
Міксини для автоматичного логування змін в моделях
"""

from django.db import models
from django.forms.models import model_to_dict
from .models import AuditLog
import json
import threading

# Сховище для поточного запиту, що дозволяє отримати користувача в моделях
_thread_locals = threading.local()


def get_current_request():
    """Отримує поточний об'єкт запиту."""
    return getattr(_thread_locals, 'request', None)


class AuditingMiddleware:
    """
    Middleware для збереження об'єкта запиту в thread-local storage.
    Його потрібно буде додати до MIDDLEWARE в settings/base.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response


class AuditMixin(models.Model):
    """
    Міксин для автоматичного логування змін в моделях.
    Додайте цей міксин до будь-якої моделі для автоматичного відстеження змін.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Перевизначений метод save з логуванням."""
        is_new = self.pk is None
        old_values = {}
        request = get_current_request()
        user = request.user if request and request.user.is_authenticated else None

        if not is_new:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                old_values = model_to_dict(old_instance)
            except self.__class__.DoesNotExist:
                is_new = True

        super().save(*args, **kwargs)

        new_values = model_to_dict(self)

        if is_new:
            AuditLog.log_action(
                user=user,
                action='CREATE',
                obj=self,
                changes={'new': self._serialize_values(new_values)},
                request=request
            )
        else:
            changes = self._get_changes(old_values, new_values)
            if changes:
                AuditLog.log_action(
                    user=user,
                    action='UPDATE',
                    obj=self,
                    changes=changes,
                    request=request
                )

    def delete(self, *args, **kwargs):
        """Перевизначений метод delete з логуванням."""
        deleted_data = model_to_dict(self)
        request = get_current_request()
        user = request.user if request and request.user.is_authenticated else None

        AuditLog.log_action(
            user=user,
            action='DELETE',
            obj=self,
            changes={'deleted': self._serialize_values(deleted_data)},
            request=request
        )

        super().delete(*args, **kwargs)

    def _serialize_values(self, values):
        """Серіалізація значень для збереження в JSON."""
        serialized = {}
        for key, value in values.items():
            serialized[key] = self._serialize_value(value)
        return serialized

    def _get_changes(self, old_values, new_values):
        """Визначення змінених полів."""
        changes = {'old': {}, 'new': {}}

        all_keys = set(old_values.keys()) | set(new_values.keys())

        for field in all_keys:
            old_value = old_values.get(field)
            new_value = new_values.get(field)

            if old_value != new_value:
                changes['old'][field] = self._serialize_value(old_value)
                changes['new'][field] = self._serialize_value(new_value)

        return changes if changes['old'] else None

    def _serialize_value(self, value):
        """Серіалізація одного значення."""
        if isinstance(value, models.Model):
            return str(value)
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        if isinstance(value, (bytes, bytearray)):
            return value.decode('utf-8', 'replace')
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)


class ViewAuditMixin:
    """Міксин для логування переглядів у Django views."""

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if hasattr(self, 'get_object'):
            try:
                obj = self.get_object()
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action='VIEW',
                    obj=obj,
                    request=request
                )
            except Exception:
                # Не перериваємо роботу, якщо об'єкт не знайдено
                pass
        return response


class SensitiveDataMixin(AuditMixin):
    """
    Міксин для моделей з чутливими даними.
    Розширює AuditMixin, додаючи перевірку змін у чутливих полях.
    """

    class Meta:
        abstract = True

    # Поля, які вважаються чутливими, повинні бути визначені в моделі-нащадку
    SENSITIVE_FIELDS = []

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        request = get_current_request()
        user = request.user if request and request.user.is_authenticated else None

        if not is_new:
            old_instance = self.__class__.objects.get(pk=self.pk)
            for field in self.SENSITIVE_FIELDS:
                old_value = getattr(old_instance, field, None)
                new_value = getattr(self, field, None)

                if old_value != new_value:
                    AuditLog.log_action(
                        user=user,
                        action='UPDATE',
                        obj=self,
                        severity='CRITICAL',
                        notes=f"Зміна чутливого поля: '{field}'",
                        changes={
                            'field': field,
                            'old': self._serialize_value(old_value),
                            'new': self._serialize_value(new_value)
                        },
                        request=request
                    )

        # Викликаємо основний метод save з AuditMixin, щоб уникнути подвійного логування
        super(AuditMixin, self).save(*args, **kwargs)