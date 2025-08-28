# apps/personnel/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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

    class Status(models.TextChoices):
        ON_DUTY = 'ON_DUTY', 'На службі'
        ON_LEAVE = 'ON_LEAVE', 'У відпустці'
        SICK_LEAVE = 'SICK_LEAVE', 'На лікуванні'
        AWOL = 'AWOL', 'СЗЧ' # Самовільне залишення частини
        DISMISSED = 'DISMISSED', 'Звільнено'
        KIA = 'KIA', 'Загинув' # Killed In Action
        MIA = 'MIA', 'Зник безвісти' # Missing In Action

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

    # Персональні дані згідно з Наказом № 280
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT, verbose_name="Військове звання")
    last_name = models.CharField("Прізвище", max_length=100)
    first_name = models.CharField("Ім'я", max_length=100)
    middle_name = models.CharField("По батькові", max_length=100, blank=True)

    personal_number = models.CharField(
        "Особистий номер (ідентифікаційний жетон)",
        max_length=20,
        unique=True,
        null=True, blank=True,
        help_text="Відповідає РНОКПП або серії та номеру паспорта"
    ) # Нове поле

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ON_DUTY
    )

    date_of_birth = models.DateField("Дата народження")
    place_of_birth = models.CharField("Місце народження", max_length=255)
    tax_id_number = models.CharField("РНОКПП", max_length=10, unique=True, null=True, blank=True)
    passport_number = models.CharField("Номер документа, що посвідчує особу", max_length=50)

    # Дані про призов/прийняття на службу (нові поля)
    enlistment_date = models.DateField("Дата призову (прийняття) на службу", null=True, blank=True)
    enlistment_authority = models.CharField("Орган, що здійснив призов (прийняття)", max_length=255, blank=True)

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

    def save(self, *args, **kwargs):
        # Автоматично заповнюємо personal_number з РНОКПП, якщо він порожній
        if not self.personal_number and self.tax_id_number:
            self.personal_number = self.tax_id_number
        super().save(*args, **kwargs)


class Education(models.Model):
    """Освіта військовослужбовця (нова модель)"""
    class EducationLevel(models.TextChoices):
        SECONDARY = 'SECONDARY', 'Повна загальна середня'
        VOCATIONAL = 'VOCATIONAL', 'Професійно-технічна'
        JUNIOR_COLLEGE = 'JUNIOR_COLLEGE', 'Фахова передвища'
        BACHELOR = 'BACHELOR', 'Бакалавр'
        MASTER = 'MASTER', 'Магістр'
        PHD = 'PHD', 'Доктор філософії'

    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='education_history')
    level = models.CharField("Рівень освіти", max_length=20, choices=EducationLevel.choices)
    institution_name = models.CharField("Назва навчального закладу", max_length=255)
    graduation_year = models.PositiveIntegerField("Рік закінчення")
    specialty = models.CharField("Спеціальність", max_length=255, blank=True)

    class Meta:
        verbose_name = "Освіта"
        verbose_name_plural = "Освіта"
        ordering = ['-graduation_year']


class FamilyMember(models.Model):
    """Член сім'ї військовослужбовця (нова модель)"""
    class RelationshipType(models.TextChoices):
        WIFE = 'WIFE', 'Дружина'
        HUSBAND = 'HUSBAND', 'Чоловік'
        SON = 'SON', 'Син'
        DAUGHTER = 'DAUGHTER', 'Донька'
        FATHER = 'FATHER', 'Батько'
        MOTHER = 'MOTHER', 'Мати'
        OTHER = 'OTHER', 'Інше'

    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='family_members')
    relationship = models.CharField("Ступінь споріднення", max_length=20, choices=RelationshipType.choices)
    last_name = models.CharField("Прізвище", max_length=100)
    first_name = models.CharField("Ім'я", max_length=100)
    middle_name = models.CharField("По батькові", max_length=100, blank=True)
    date_of_birth = models.DateField("Дата народження")
    address = models.CharField("Адреса проживання", max_length=255, blank=True)

    class Meta:
        verbose_name = "Член сім'ї"
        verbose_name_plural = "Члени сім'ї"

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
        ENLISTMENT = 'ENLISTMENT', 'Зарахування на службу'
        APPOINTMENT = 'APPOINTMENT', 'Призначення на посаду'
        TRANSFER = 'TRANSFER', 'Переведення'
        PROMOTION = 'PROMOTION', 'Підвищення у званні'
        DISMISSAL = 'DISMISSAL', 'Звільнення'
        DEATH = 'DEATH', 'Загибель/Смерть'

    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='service_history')
    event_type = models.CharField("Тип події", max_length=20, choices=EventType.choices)
    event_date = models.DateField("Дата події")
    details = models.JSONField("Деталі", default=dict, help_text="Зберігає деталі, напр. new_rank, new_position")
    order_reference = models.CharField("Посилання на наказ", max_length=255)

    class Meta:
        verbose_name = "Подія в історії служби"
        verbose_name_plural = "Історія служби"
        ordering = ['-event_date']


class PositionHistory(models.Model):
    """
    Історія перебування військовослужбовця на посадах.
    Забезпечує повний аудиторський слід кар'єрного шляху.
    """
    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, related_name='position_history', verbose_name="Військовослужбовець")
    position = models.ForeignKey('staffing.Position', on_delete=models.PROTECT, verbose_name="Посада")
    start_date = models.DateField("Дата призначення")
    end_date = models.DateField("Дата звільнення з посади", null=True, blank=True)
    order_reference = models.CharField("Посилання на наказ", max_length=255)

    class Meta:
        verbose_name = "Історія посад"
        verbose_name_plural = "Історії посад"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.serviceman} - {self.position.name} ({self.start_date})"

    def clean(self):
        # Перевірка, що дата закінчення не раніше дати початку
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('Дата звільнення з посади не може бути раніше дати призначення.')


class TemporaryArrival(models.Model):
    """
    Облік тимчасово прибулого особового складу з інших військових частин.
    """
    full_name = models.CharField("ПІБ", max_length=255)
    rank_name = models.CharField("Військове звання", max_length=100)
    position_name = models.CharField("Посада", max_length=255)

    origin_unit = models.CharField("Звідки прибув (в/ч, населений пункт)", max_length=255)
    arrival_reason = models.CharField("Підстава прибуття (наказ, розпорядження)", max_length=255)

    arrival_date = models.DateField("Дата прибуття")
    arrival_order = models.CharField("Наказ про прибуття (дата і номер)", max_length=100, blank=True)

    departure_date = models.DateField("Дата вибуття", null=True, blank=True)
    departure_order = models.CharField("Наказ про вибуття (дата і номер)", max_length=100, blank=True)

    notes = models.TextField("Додаткова інформація", blank=True)

    class Meta:
        verbose_name = "Тимчасово прибулий"
        verbose_name_plural = "4. Тимчасово прибулі"
        ordering = ['-arrival_date']

    def __str__(self):
        return f"{self.rank_name} {self.full_name} (прибув {self.arrival_date})"


class IrrecoverableLoss(models.Model):
    """
    Облік безповоротних втрат особового складу.
    """

    class LossType(models.TextChoices):
        KIA = 'KIA', 'Загинув'
        DIED = 'DIED', 'Помер (від хвороби, нещасного випадку)'
        MIA = 'MIA', 'Зник безвісти'
        CAPTURED = 'CAPTURED', 'Полонений'

    serviceman = models.OneToOneField(
        Serviceman,
        on_delete=models.CASCADE,
        related_name='loss_record',
        verbose_name="Військовослужбовець"
    )

    loss_type = models.CharField("Вид втрати", max_length=10, choices=LossType.choices)
    loss_date = models.DateField("Дата безповоротної втрати")
    circumstances = models.TextField("Обставини, що призвели до втрати")
    loss_location = models.CharField("Місце втрати", max_length=255)

    exclusion_date = models.DateField("Дата виключення зі списків")
    exclusion_order = models.CharField("Наказ про виключення (дата і номер)", max_length=100)

    notification_details = models.CharField(
        "Кому, за яким номером і коли надіслано сповіщення",
        max_length=255,
        blank=True
    )
    burial_location = models.CharField(
        "Місце і дата поховання (імовірне місце перебування)",
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = "Безповоротна втрата"
        verbose_name_plural = "7. Безповоротні втрати"
        ordering = ['-loss_date']

    def __str__(self):
        return f"{self.get_loss_type_display()} - {self.serviceman.full_name}"