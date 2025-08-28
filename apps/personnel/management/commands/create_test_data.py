# apps/personnel/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import random
from apps.personnel.models import Rank, Serviceman, Contract, ServiceHistoryEvent, Education, FamilyMember
from apps.documents.models import ServicemanReport
from apps.staffing.models import Unit, MilitarySpecialty, Position

User = get_user_model()


class Command(BaseCommand):
    help = 'Створює тестові дані для системи обліку особового складу'

    def handle(self, *args, **options):
        self.stdout.write('Початок створення тестових даних...')

        if input('Видалити існуючі дані? Це призведе до повної очистки! (y/n): ').lower() == 'y':
            self.clear_data()

        self.create_base_data()
        self.create_personnel_data()

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно створено!'))

    def clear_data(self):
        self.stdout.write('Видалення існуючих даних...')
        # Видаляємо в порядку залежностей
        ServicemanReport.objects.all().delete()
        ServiceHistoryEvent.objects.all().delete()
        Contract.objects.all().delete()
        FamilyMember.objects.all().delete()
        Education.objects.all().delete()
        Serviceman.objects.all().delete()
        Position.objects.all().delete()
        Unit.objects.all().delete()
        MilitarySpecialty.objects.all().delete()
        Rank.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_base_data(self):
        self.stdout.write('Створення базових довідників (звання, ВОС, підрозділи)...')
        # Звання
        ranks_data = [('Солдат', 1), ('Старший солдат', 2), ('Молодший сержант', 3), ('Сержант', 4),
                      ('Старший сержант', 5), ('Молодший лейтенант', 11), ('Лейтенант', 12), ('Старший лейтенант', 13),
                      ('Капітан', 14), ('Майор', 15), ('Підполковник', 16), ('Полковник', 17)]
        for name, order in ranks_data:
            Rank.objects.get_or_create(name=name, defaults={'order': order})

        # ВОС
        specialties_data = [('100100', 'Стрілець'), ('100300', 'Командир взводу'), ('100400', 'Командир роти')]
        for code, name in specialties_data:
            MilitarySpecialty.objects.get_or_create(code=code, defaults={'name': name})

        # Підрозділи
        brigade, _ = Unit.objects.get_or_create(name='24-та ОМБр', parent=None)
        battalion_1, _ = Unit.objects.get_or_create(name='1-й механізований батальйон', parent=brigade)
        company_1, _ = Unit.objects.get_or_create(name='1-ша механізована рота', parent=battalion_1)
        Unit.objects.get_or_create(name='1-й механізований взвод', parent=company_1)

    def create_personnel_data(self):
        self.stdout.write('Створення посад, особового складу та пов\'язаних даних...')

        # Створюємо посади
        company = Unit.objects.get(name='1-ша механізована рота')
        specialty = MilitarySpecialty.objects.get(code='100100')
        positions_to_create = []
        if not Position.objects.exists():
            for i in range(30):
                positions_to_create.append(
                    Position(position_index=f'П-{i + 1:05d}', unit=company, name=f'Стрілець {i + 1}', category='Солдат',
                             specialty=specialty, tariff_rate='4')
                )
            Position.objects.bulk_create(positions_to_create)
            self.stdout.write(f'Створено {len(positions_to_create)} посад')

        # Створюємо військовослужбовців
        if not Serviceman.objects.exists():
            ranks = {rank.name: rank for rank in Rank.objects.all()}
            # Беремо 20 випадкових вільних посад
            vacant_positions = list(Position.objects.filter(serviceman__isnull=True).order_by('?')[:20])

            for i, position in enumerate(vacant_positions):
                # ВИПРАВЛЕНО: Гарантований 10-значний унікальний номер
                start_range = 2000000000
                tax_id = str(start_range + i)

                sm = Serviceman.objects.create(
                    rank=ranks[position.category],
                    last_name=f'Прізвище{i}',
                    first_name=f'Ім\'я{i}',
                    middle_name=f'По-батькові{i}',
                    date_of_birth=date(1995, 1, 1),
                    place_of_birth='м. Київ',
                    passport_number=f'АА10000{i}',
                    tax_id_number=tax_id,
                    personal_number=tax_id,
                    enlistment_date=date(2023, 3, 1),
                    enlistment_authority='Київський МТЦК та СП',
                    position=position
                )
                Education.objects.create(serviceman=sm, level=Education.EducationLevel.SECONDARY,
                                         institution_name='ЗОШ №1', graduation_year=2012)
                FamilyMember.objects.create(serviceman=sm, relationship=FamilyMember.RelationshipType.WIFE,
                                            last_name=f'Прізвище{i}', first_name='Марія', middle_name='Іванівна',
                                            date_of_birth=date(1996, 1, 1))

            self.stdout.write(f'Створено {Serviceman.objects.count()} військовослужбовців')

        # Створюємо контракти, історію служби та рапорти
        all_servicemen = list(Serviceman.objects.all())
        if all_servicemen and not Contract.objects.exists():
            for sm in all_servicemen:
                Contract.objects.create(serviceman=sm, start_date=sm.enlistment_date,
                                        end_date=sm.enlistment_date.replace(year=sm.enlistment_date.year + 3))
            self.stdout.write(f'Створено {Contract.objects.count()} контрактів')

        if all_servicemen and not ServiceHistoryEvent.objects.exists():
            for sm in all_servicemen:
                ServiceHistoryEvent.objects.create(serviceman=sm, event_type=ServiceHistoryEvent.EventType.ENLISTMENT,
                                                   event_date=sm.enlistment_date, order_reference='Наказ ТЦК №1')
            self.stdout.write(f'Створено {ServiceHistoryEvent.objects.count()} записів в історії служби')

        if all_servicemen and not ServicemanReport.objects.exists():
            for i in range(5):
                ServicemanReport.objects.create(
                    registration_number=f'РАП-{i + 1:04d}',
                    submission_date=date.today() - timedelta(days=random.randint(1, 20)),
                    report_type=random.choice(ServicemanReport.ReportType.choices)[0],
                    status=random.choice(
                        [ServicemanReport.ReportStatus.SUBMITTED, ServicemanReport.ReportStatus.UNDER_REVIEW]),
                    author=random.choice(all_servicemen),
                    recipient_position="Командиру 1-ї механізованої роти",
                    summary=f"Тестовий рапорт №{i + 1}"
                )
            self.stdout.write(f'Створено {ServicemanReport.objects.count()} рапортів')