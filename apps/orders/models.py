# apps/orders/models.py
from django.db import models
from django.conf import settings
from apps.personnel.models import Serviceman

class Order(models.Model):
    """
    Модель для зберігання наказів.
    Фіксує офіційні кадрові рішення.
    """
    class OrderType(models.TextChoices):
        PERSONNEL = 'PERSONNEL', 'По особовому складу'
        SERVICE = 'SERVICE', 'По стройовій частині'

    class OrderStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Проєкт'
        ON_APPROVAL = 'ON_APPROVAL', 'На погодженні'
        SIGNED = 'SIGNED', 'Підписано'
        EXECUTED = 'EXECUTED', 'Виконано'
        CANCELED = 'CANCELED', 'Скасовано'

    order_number = models.CharField("Номер наказу", max_length=100)
    order_date = models.DateField("Дата наказу")
    order_type = models.CharField("Тип наказу", max_length=20, choices=OrderType.choices)
    issuing_authority = models.CharField("Орган, що видав наказ", max_length=255)
    status = models.CharField("Статус", max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT)
    order_text = models.TextField("Повний текст наказу", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        verbose_name="Створив"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Наказ"
        verbose_name_plural = "Накази"
        ordering = ['-order_date', '-order_number']

    def __str__(self):
        return f"Наказ №{self.order_number} від {self.order_date}"

class OrderAction(models.Model):
    """
    Деталізація конкретної дії в межах одного наказу.
    """
    class ActionType(models.TextChoices):
        APPOINT = 'APPOINT', 'Призначити'
        TRANSFER = 'TRANSFER', 'Перевести'
        PROMOTE = 'PROMOTE', 'Присвоїти звання'
        DISMISS = 'DISMISS', 'Звільнити'
        AWARD = 'AWARD', 'Нагородити'
        REPRIMAND = 'REPRIMAND', 'Оголосити догану'
        EXCLUDE_KIA = 'EXCLUDE_KIA', 'Виключити як загиблого'
        # Додайте інші типи дій за потреби

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='actions', verbose_name="Наказ")
    personnel = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='order_actions', verbose_name="Особа")
    action_type = models.CharField("Тип дії", max_length=20, choices=ActionType.choices)
    details = models.JSONField(
        "Деталі дії",
        default=dict,
        blank=True,
        help_text="Зберігає контекстно-залежні дані, наприклад, ID нової посади для призначення"
    )
    execution_status = models.BooleanField("Статус виконання", default=False)

    class Meta:
        verbose_name = "Дія за наказом"
        verbose_name_plural = "Дії за наказами"
        ordering = ['order']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.personnel} (Наказ №{self.order.order_number})"