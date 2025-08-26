from django.db import models
from django.conf import settings

class Rank(models.Model):
    """Військове звання - довідник"""
    name = models.CharField("Назва звання", max_length=100, unique=True)
    order = models.PositiveIntegerField("Порядок сортування", default=0)

    class Meta:
        verbose_name = "Військове звання"
        verbose_name_plural = "Військові звання"
        ordering = ['order']

    def __str__(self):
        return self.name

class Serviceman(models.Model):
    """Військовослужбовець - центральна модель персонального обліку"""
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
    """Контракт військовослужбовця"""
    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField("Дата укладення контракту")
    end_date = models.DateField("Дата закінчення контракту")
    details = models.TextField("Деталі контракту", blank=True)

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракти"
        ordering = ['-start_date']

class ServiceHistoryEvent(models.Model):
    """Журнал подій в історії служби"""
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