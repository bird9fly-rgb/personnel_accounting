from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Unit(MPTTModel):
    """Підрозділ (військова частина, батальйон, рота тощо)"""
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
    """Військово-облікова спеціальність (ВОС) - довідник"""
    code = models.CharField("Код ВОС", max_length=20, unique=True)
    name = models.CharField("Найменування", max_length=255)

    class Meta:
        verbose_name = "Військово-облікова спеціальність"
        verbose_name_plural = "Військово-облікові спеціальності"

    def __str__(self):
        return f"{self.code} - {self.name}"

class Position(models.Model):
    """Посада згідно зі штатом"""
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