# apps/personnel/management/commands/create_test_data.py
"""
Management command для створення тестових даних для АСООС 'ОБРІГ'
Використання: python manage.py create_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random
from apps.personnel.models import Rank, Serviceman, Contract, ServiceHistoryEvent
from apps.staffing.models import Unit, MilitarySpecialty, Position
from apps.orders.models import Order, OrderAction

User = get_user_model()


class Command(BaseCommand):
    help = 'Створює тестові дані для системи обліку особового складу'

    def handle(self, *args, **options):
        self.stdout.write('Початок створення тестових даних...')

        # Очистка існуючих даних (опціонально)
        if input('Видалити існуючі дані? (y/n): ').lower() == 'y':
            self.clear_data()

        # Створення даних
        self.create_users()
        self.create_ranks()
        self.create_specialties()
        self.create_units()
        self.create_positions()
        self.create_servicemen()
        self.create_contracts()
        self.create_service_history()
        self.create_orders()  # <-- Додано створення наказів

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно створено!'))

    def clear_data(self):
        """Видалення існуючих даних"""
        self.stdout.write('Видалення існуючих даних...')
        OrderAction.objects.all().delete()
        Order.objects.all().delete()
        ServiceHistoryEvent.objects.all().delete()
        Contract.objects.all().delete()
        Serviceman.objects.all().delete()
        Position.objects.all().delete()
        Unit.objects.all().delete()
        MilitarySpecialty.objects.all().delete()
        Rank.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self):
        """Створення тестових користувачів"""
        self.stdout.write('Створення користувачів...')

        # Адміністратор
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mil.gov.ua',
                'first_name': 'Адмін',
                'last_name': 'Системи',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Кадровий офіцер
        hr_officer, created = User.objects.get_or_create(
            username='hr_officer',
            defaults={
                'email': 'hr@mil.gov.ua',
                'first_name': 'Петро',
                'last_name': 'Кадровик',
                'middle_name': 'Іванович',
                'is_staff': True
            }
        )
        if created:
            hr_officer.set_password('hr123')
            hr_officer.save()

        # Командир
        commander, created = User.objects.get_or_create(
            username='commander',
            defaults={
                'email': 'commander@mil.gov.ua',
                'first_name': 'Василь',
                'last_name': 'Командир',
                'middle_name': 'Петрович',
                'is_staff': False
            }
        )
        if created:
            commander.set_password('commander123')
            commander.save()

        self.stdout.write(f'Створено {User.objects.count()} користувачів')

    def create_ranks(self):
        """Створення військових звань"""
        self.stdout.write('Створення військових звань...')
        ranks_data = [('Солдат', 1), ('Старший солдат', 2), ('Молодший сержант', 3), ('Сержант', 4),
                      ('Старший сержант', 5), ('Головний сержант', 6), ('Штаб-сержант', 7), ('Майстер-сержант', 8),
                      ('Старший майстер-сержант', 9), ('Головний майстер-сержант', 10), ('Молодший лейтенант', 11),
                      ('Лейтенант', 12), ('Старший лейтенант', 13), ('Капітан', 14), ('Майор', 15),
                      ('Підполковник', 16), ('Полковник', 17), ('Бригадний генерал', 18), ('Генерал-майор', 19),
                      ('Генерал-лейтенант', 20), ('Генерал', 21)]
        for name, order in ranks_data:
            Rank.objects.get_or_create(name=name, defaults={'order': order})
        self.stdout.write(f'Створено {Rank.objects.count()} військових звань')

    def create_specialties(self):
        """Створення військово-облікових спеціальностей"""
        self.stdout.write('Створення ВОС...')
        specialties_data = [('100100', 'Стрілець'), ('100101', 'Кулеметник'), ('100102', 'Гранатометник'),
                            ('100103', 'Снайпер'), ('100200', 'Командир відділення'), ('100300', 'Командир взводу'),
                            ('100400', 'Командир роти'), ('100500', 'Командир батальйону'),
                            ('200100', 'Механік-водій БМП'), ('200200', 'Навідник-оператор'),
                            ('300100', 'Зв\'язківець'), ('300200', 'Радіотелефоніст'),
                            ('400100', 'Санітарний інструктор'), ('400200', 'Фельдшер'), ('500100', 'Кухар'),
                            ('500200', 'Водій'), ('600100', 'Інженер-сапер'), ('700100', 'Артилерист'),
                            ('800100', 'Оператор БПЛА'), ('900100', 'Штабний офіцер')]
        for code, name in specialties_data:
            MilitarySpecialty.objects.get_or_create(code=code, defaults={'name': name})
        self.stdout.write(f'Створено {MilitarySpecialty.objects.count()} ВОС')

    def create_units(self):
        """Створення структури підрозділів"""
        self.stdout.write('Створення підрозділів...')
        brigade, _ = Unit.objects.get_or_create(name='24-та окрема механізована бригада імені короля Данила',
                                                parent=None)
        battalion_1, _ = Unit.objects.get_or_create(name='1-й механізований батальйон', parent=brigade)
        battalion_2, _ = Unit.objects.get_or_create(name='2-й механізований батальйон', parent=brigade)
        tank_battalion, _ = Unit.objects.get_or_create(name='Танковий батальйон', parent=brigade)
        artillery, _ = Unit.objects.get_or_create(name='Артилерійський дивізіон', parent=brigade)
        support, _ = Unit.objects.get_or_create(name='Батальйон забезпечення', parent=brigade)
        for i in range(1, 4):
            company, _ = Unit.objects.get_or_create(name=f'{i}-та механізована рота', parent=battalion_1)
            for j in range(1, 4):
                platoon, _ = Unit.objects.get_or_create(name=f'{j}-й механізований взвод', parent=company)
                for k in range(1, 4):
                    Unit.objects.get_or_create(name=f'{k}-те відділення', parent=platoon)
        self.stdout.write(f'Створено/перевірено {Unit.objects.count()} підрозділів')

    def create_positions(self):
        """Створення штатних посад"""
        self.stdout.write('Створення штатних посад...')
        position_counter = 1
        brigade = Unit.objects.get(name='24-та окрема механізована бригада імені короля Данила')
        positions_data = [(brigade, 'Командир бригади', 'Полковник', '100500', '24'),
                          (brigade, 'Заступник командира бригади', 'Підполковник', '100500', '23'),
                          (brigade, 'Начальник штабу', 'Підполковник', '900100', '23')]
        for company in Unit.objects.filter(name__contains='рота'):
            positions_data.extend([(company, 'Командир роти', 'Капітан', '100400', '21'),
                                   (company, 'Заступник командира роти', 'Старший лейтенант', '100400', '20')])
        for platoon in Unit.objects.filter(name__contains='взвод'):
            positions_data.extend([(platoon, 'Командир взводу', 'Лейтенант', '100300', '19')])
        for squad in Unit.objects.filter(name__contains='відділення'):
            positions_data.extend([(squad, 'Командир відділення', 'Сержант', '100200', '10'),
                                   (squad, 'Стрілець', 'Солдат', '100100', '5')])
        for unit, position_name, category, specialty_code, tariff in positions_data:
            specialty = MilitarySpecialty.objects.get(code=specialty_code)
            Position.objects.get_or_create(position_index=f'П-{position_counter:05d}',
                                           defaults={'unit': unit, 'name': position_name, 'category': category,
                                                     'specialty': specialty, 'tariff_rate': tariff})
            position_counter += 1
        self.stdout.write(f'Створено {Position.objects.count()} штатних посад')

    def create_servicemen(self):
        """Створення військовослужбовців"""
        self.stdout.write('Створення військовослужбовців...')
        last_names = ['Шевченко', 'Коваленко', 'Бондаренко', 'Ткаченко', 'Кравченко']
        first_names_male = ['Олександр', 'Михайло', 'Іван', 'Петро', 'Василь']
        middle_names_male = ['Олександрович', 'Михайлович', 'Іванович', 'Петрович', 'Васильович']
        cities = ['Київ', 'Харків', 'Одеса', 'Дніпро', 'Львів']
        positions = list(Position.objects.filter(serviceman__isnull=True))
        ranks = {rank.name: rank for rank in Rank.objects.all()}
        filled_positions = random.sample(positions, k=min(len(positions), int(Position.objects.count() * 0.7)))
        for i, position in enumerate(filled_positions):
            rank_name = position.category
            if rank_name not in ranks:
                rank_name = 'Солдат'
            rank = ranks[rank_name]
            tax_id = f'{random.randint(2000000000, 3999999999)}'
            serviceman, created = Serviceman.objects.get_or_create(
                tax_id_number=tax_id,
                defaults={
                    'rank': rank,
                    'last_name': random.choice(last_names),
                    'first_name': random.choice(first_names_male),
                    'middle_name': random.choice(middle_names_male),
                    'date_of_birth': date(random.randint(1985, 2005), random.randint(1, 12), random.randint(1, 28)),
                    'place_of_birth': f'м. {random.choice(cities)}',
                    'passport_number': f'АА{random.randint(100000, 999999)}'
                }
            )
            if created:
                position.serviceman = serviceman
                position.save()
                serviceman.position = position
                serviceman.save()
        self.stdout.write(f'Створено {Serviceman.objects.count()} військовослужбовців')

    def create_contracts(self):
        """Створення контрактів"""
        self.stdout.write('Створення контрактів...')
        for serviceman in Serviceman.objects.all():
            if not serviceman.contracts.exists():
                contract_years = 5 if serviceman.rank.order >= 11 else 3
                start_date = date.today() - timedelta(days=random.randint(30, 365 * 2))
                end_date = start_date + timedelta(days=365 * contract_years)
                # Створюємо один контракт, що скоро закінчиться
                if serviceman.id % 10 == 0:
                    end_date = date.today() + timedelta(days=random.randint(15, 80))
                # Створюємо один протермінований контракт
                if serviceman.id % 15 == 0:
                    end_date = date.today() - timedelta(days=random.randint(15, 80))

                Contract.objects.create(serviceman=serviceman, start_date=start_date, end_date=end_date,
                                        details=f'Контракт на {contract_years} років')
        self.stdout.write(f'Створено {Contract.objects.count()} контрактів')

    def create_service_history(self):
        """Створення історії служби"""
        self.stdout.write('Створення історії служби...')
        for serviceman in Serviceman.objects.filter(service_history__isnull=True).select_related('position'):
            if serviceman.contracts.exists():
                ServiceHistoryEvent.objects.create(
                    serviceman=serviceman,
                    event_type=ServiceHistoryEvent.EventType.ENLISTMENT,
                    event_date=serviceman.contracts.first().start_date,
                    details={'source': 'ТЦК та СП'},
                    order_reference=f'Наказ ТЦК №{random.randint(100, 200)}'
                )
                ServiceHistoryEvent.objects.create(
                    serviceman=serviceman,
                    event_type=ServiceHistoryEvent.EventType.APPOINTMENT,
                    event_date=serviceman.contracts.first().start_date + timedelta(days=1),
                    details={'position_name': str(serviceman.position)},
                    order_reference=f'Наказ в/ч №{random.randint(1, 50)}'
                )
        self.stdout.write(f'Створено {ServiceHistoryEvent.objects.count()} записів історії служби')

    def create_orders(self):
        """Створення тестових наказів"""
        self.stdout.write('Створення наказів...')
        hr_user = User.objects.get(username='hr_officer')
        servicemen = list(Serviceman.objects.all())
        ranks = list(Rank.objects.all())
        vacant_positions = list(Position.objects.filter(serviceman__isnull=True))

        if not servicemen:
            self.stdout.write(self.style.WARNING('Немає військовослужбовців для створення наказів.'))
            return

        # Наказ про призначення
        order1, _ = Order.objects.get_or_create(
            order_number='101-TP',
            defaults={
                'order_date': date.today() - timedelta(days=30),
                'order_type': Order.OrderType.PERSONNEL,
                'issuing_authority': 'Командир в/ч А0001',
                'status': Order.OrderStatus.EXECUTED,
                'created_by': hr_user
            }
        )
        if vacant_positions:
            OrderAction.objects.get_or_create(
                order=order1,
                personnel=random.choice(servicemen),
                action_type=OrderAction.ActionType.APPOINT,
                details={'new_position_id': random.choice(vacant_positions).id}
            )

        # Наказ про присвоєння звання
        order2, _ = Order.objects.get_or_create(
            order_number='102-TP',
            defaults={
                'order_date': date.today() - timedelta(days=15),
                'order_type': Order.OrderType.PERSONNEL,
                'issuing_authority': 'Командувач ОК "Захід"',
                'status': Order.OrderStatus.SIGNED,
                'created_by': hr_user
            }
        )
        serviceman_to_promote = random.choice(servicemen)
        current_rank_index = list(ranks).index(serviceman_to_promote.rank)
        if current_rank_index + 1 < len(ranks):
            new_rank = ranks[current_rank_index + 1]
            OrderAction.objects.get_or_create(
                order=order2,
                personnel=serviceman_to_promote,
                action_type=OrderAction.ActionType.PROMOTE,
                details={'new_rank_id': new_rank.id}
            )

        self.stdout.write(f'Створено {Order.objects.count()} наказів')