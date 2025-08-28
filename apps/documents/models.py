# apps/documents/models.py
import os
from django.db import models
from django.conf import settings
from apps.personnel.models import Serviceman


def report_attachment_path(instance, filename):
    """Генерує шлях для збереження файлу: media/reports/{рік}/{місяць}/{номер_рапорту}/{назва_файлу}"""
    date = instance.submission_date
    return f'reports/{date.year}/{date.month}/{instance.registration_number}/{filename}'


class ServicemanReport(models.Model):
    """
    Модель для зберігання рапортів військовослужбовців.
    Фіксує офіційні запити та звернення особового складу.
    """

    class ReportType(models.TextChoices):
        LEAVE = 'LEAVE', 'Рапорт на відпустку'
        TRANSFER = 'TRANSFER', 'Рапорт на переведення'
        DISMISSAL = 'DISMISSAL', 'Рапорт на звільнення'
        FINANCIAL = 'FINANCIAL', 'Фінансовий рапорт'
        MATERIAL = 'MATERIAL', 'Рапорт на матеріальне забезпечення'
        OTHER = 'OTHER', 'Інший рапорт'

    class ReportStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Проєкт'
        SUBMITTED = 'SUBMITTED', 'Подано'
        UNDER_REVIEW = 'UNDER_REVIEW', 'На розгляді'
        APPROVED = 'APPROVED', 'Затверджено'
        REJECTED = 'REJECTED', 'Відхилено'
        ARCHIVED = 'ARCHIVED', 'В архіві'

    # Основні дані рапорту
    registration_number = models.CharField("Реєстраційний номер", max_length=100, unique=True,
                                           help_text="Номер, що присвоюється при реєстрації в частині")
    submission_date = models.DateField("Дата подання")
    report_type = models.CharField("Тип рапорту", max_length=20, choices=ReportType.choices)
    status = models.CharField("Статус", max_length=20, choices=ReportStatus.choices, default=ReportStatus.SUBMITTED)

    # Хто і кому подає рапорт
    author = models.ForeignKey(
        Serviceman,
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name="Автор рапорту"
    )
    recipient_position = models.CharField("Посада отримувача", max_length=255,
                                          help_text="Наприклад, 'Командиру 1-ї механізованої роти'")

    # Зміст
    summary = models.CharField("Короткий зміст (тема)", max_length=255)
    full_text = models.TextField("Повний текст рапорту", blank=True)

    # Нове поле для прикріпленого файлу
    attachment = models.FileField(
        "Прикріплений файл",
        upload_to=report_attachment_path,
        null=True,
        blank=True,
        help_text="Додайте скан-копію рапорту або інші супровідні документи"
    )

    # Обробка та відповідь
    resolution = models.TextField("Резолюція / Рішення по рапорту", blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_reports',
        verbose_name="Хто розглянув"
    )

    # Системна інформація
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рапорт"
        verbose_name_plural = "Рапорти військовослужбовців"
        ordering = ['-submission_date']

    def __str__(self):
        return f"Рапорт №{self.registration_number} від {self.author} від {self.submission_date}"

    @property
    def attachment_filename(self):
        """Повертає тільки ім'я файлу зі шляху."""
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return ""