# apps/auditing/models.py
"""
Моделі для системи аудиту та журналювання
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """Модель для зберігання журналу аудиту всіх змін в системі"""

    ACTION_CHOICES = [
        ('CREATE', 'Створено'),
        ('UPDATE', 'Оновлено'),
        ('DELETE', 'Видалено'),
        ('VIEW', 'Переглянуто'),
        ('EXPORT', 'Експортовано'),
        ('LOGIN', 'Вхід в систему'),
        ('LOGOUT', 'Вихід з системи'),
        ('PERMISSION_CHANGE', 'Зміна прав доступу'),
    ]

    SEVERITY_CHOICES = [
        ('INFO', 'Інформація'),
        ('WARNING', 'Попередження'),
        ('ERROR', 'Помилка'),
        ('CRITICAL', 'Критично'),
    ]

    # Користувач, який виконав дію
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Користувач",
        related_name='audit_logs'
    )

    # Тип дії
    action = models.CharField(
        "Дія",
        max_length=20,
        choices=ACTION_CHOICES
    )

    # Час виконання дії
    timestamp = models.DateTimeField(
        "Час події",
        default=timezone.now,
        db_index=True
    )

    # Generic relation до будь-якої моделі
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Тип об'єкта"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID об'єкта"
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Додаткова інформація
    object_repr = models.CharField(
        "Представлення об'єкта",
        max_length=255,
        help_text="Текстове представлення об'єкта на момент дії"
    )

    changes = models.JSONField(
        "Зміни",
        default=dict,
        blank=True,
        help_text="JSON з старими та новими значеннями"
    )

    # Контекстна інформація
    ip_address = models.GenericIPAddressField(
        "IP адреса",
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        "User Agent",
        blank=True
    )

    session_key = models.CharField(
        "Ключ сесії",
        max_length=40,
        blank=True
    )

    # Рівень важливості
    severity = models.CharField(
        "Важливість",
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='INFO'
    )

    # Додаткові примітки
    notes = models.TextField(
        "Примітки",
        blank=True
    )

    class Meta:
        verbose_name = "Запис аудиту"
        verbose_name_plural = "Журнал аудиту"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.object_repr} - {self.timestamp}"

    def get_changes_display(self):
        """Форматований вивід змін"""
        if not self.changes:
            return "Немає змін"

        old_values = self.changes.get('old', {})
        new_values = self.changes.get('new', {})

        changes_list = []
        for field, new_value in new_values.items():
            old_value = old_values.get(field, '—')
            if old_value != new_value:
                changes_list.append(f"{field}: {old_value} → {new_value}")

        return '\n'.join(changes_list)

    @classmethod
    def log_action(cls, user, action, obj=None, changes=None, request=None, severity='INFO', notes=''):
        """Утиліта для швидкого створення запису аудиту"""
        log_entry = cls(
            user=user,
            action=action,
            severity=severity,
            notes=notes
        )

        if obj:
            log_entry.content_object = obj
            log_entry.object_repr = str(obj)

        if changes:
            log_entry.changes = changes

        if request:
            log_entry.ip_address = cls.get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')
            if hasattr(request, 'session'):
                log_entry.session_key = request.session.session_key or ''

        log_entry.save()
        return log_entry

    @staticmethod
    def get_client_ip(request):
        """Отримання IP адреси клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityEvent(models.Model):
    """Модель для зберігання подій безпеки"""

    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Успішний вхід'),
        ('LOGIN_FAILED', 'Невдалий вхід'),
        ('PASSWORD_CHANGE', 'Зміна пароля'),
        ('PASSWORD_RESET', 'Скидання пароля'),
        ('PERMISSION_DENIED', 'Відмова в доступі'),
        ('SUSPICIOUS_ACTIVITY', 'Підозріла активність'),
        ('DATA_EXPORT', 'Експорт даних'),
        ('BULK_OPERATION', 'Масова операція'),
    ]

    event_type = models.CharField(
        "Тип події",
        max_length=30,
        choices=EVENT_TYPES
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Користувач"
    )

    timestamp = models.DateTimeField(
        "Час події",
        auto_now_add=True,
        db_index=True
    )

    ip_address = models.GenericIPAddressField(
        "IP адреса"
    )

    details = models.JSONField(
        "Деталі",
        default=dict
    )

    is_resolved = models.BooleanField(
        "Вирішено",
        default=False
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_security_events',
        verbose_name="Вирішено користувачем"
    )

    resolved_at = models.DateTimeField(
        "Час вирішення",
        null=True,
        blank=True
    )

    resolution_notes = models.TextField(
        "Примітки до вирішення",
        blank=True
    )

    class Meta:
        verbose_name = "Подія безпеки"
        verbose_name_plural = "Події безпеки"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"


class DataExportLog(models.Model):
    """Журнал експорту даних"""

    EXPORT_FORMATS = [
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
        ('PDF', 'PDF'),
        ('JSON', 'JSON'),
        ('XML', 'XML'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Користувач"
    )

    timestamp = models.DateTimeField(
        "Час експорту",
        auto_now_add=True
    )

    model_name = models.CharField(
        "Модель",
        max_length=100
    )

    format = models.CharField(
        "Формат",
        max_length=10,
        choices=EXPORT_FORMATS
    )

    records_count = models.PositiveIntegerField(
        "Кількість записів"
    )

    filters_applied = models.JSONField(
        "Застосовані фільтри",
        default=dict,
        blank=True
    )

    file_path = models.CharField(
        "Шлях до файлу",
        max_length=500,
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        "IP адреса",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Лог експорту даних"
        verbose_name_plural = "Логи експорту даних"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.model_name} - {self.format} - {self.timestamp}"