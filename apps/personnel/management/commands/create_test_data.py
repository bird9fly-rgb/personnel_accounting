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

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно створено!'))

    def clear_data(self):
        """Видалення існуючих даних"""
        self.stdout.write('Видалення існуючих даних...')
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

        ranks_data = [
            # Солдати
            ('Солдат', 1),
            ('Старший солдат', 2),

            # Сержанти
            ('Молодший сержант', 3),
            ('Сержант', 4),
            ('Старший сержант', 5),
            ('Головний сержант', 6),
            ('Штаб-сержант', 7),
            ('Майстер-сержант', 8),
            ('Старший майстер-сержант', 9),
            ('Головний майстер-сержант', 10),

            # Офіцери
            ('Молодший лейтенант', 11),
            ('Лейтенант', 12),
            ('Старший лейтенант', 13),
            ('Капітан', 14),
            ('Майор', 15),
            ('Підполковник', 16),
            ('Полковник', 17),
            ('Бригадний генерал', 18),
            ('Генерал-майор', 19),
            ('Генерал-лейтенант', 20),
            ('Генерал', 21),
        ]

        for name, order in ranks_data:
            Rank.objects.get_or_create(name=name, defaults={'order': order})

        self.stdout.write(f'Створено {Rank.objects.count()} військових звань')

    def create_specialties(self):
        """Створення військово-облікових спеціальностей"""
        self.stdout.write('Створення ВОС...')

        specialties_data = [
            ('100100', 'Стрілець'),
            ('100101', 'Кулеметник'),
            ('100102', 'Гранатометник'),
            ('100103', 'Снайпер'),
            ('100200', 'Командир відділення'),
            ('100300', 'Командир взводу'),
            ('100400', 'Командир роти'),
            ('100500', 'Командир батальйону'),
            ('200100', 'Механік-водій БМП'),
            ('200200', 'Навідник-оператор'),
            ('300100', 'Зв\'язківець'),
            ('300200', 'Радіотелефоніст'),
            ('400100', 'Санітарний інструктор'),
            ('400200', 'Фельдшер'),
            ('500100', 'Кухар'),
            ('500200', 'Водій'),
            ('600100', 'Інженер-сапер'),
            ('700100', 'Артилерист'),
            ('800100', 'Оператор БПЛА'),
            ('900100', 'Штабний офіцер'),
        ]

        for code, name in specialties_data:
            MilitarySpecialty.objects.get_or_create(code=code, defaults={'name': name})

        self.stdout.write(f'Створено {MilitarySpecialty.objects.count()} ВОС')

    def create_units(self):
        """Створення структури підрозділів"""
        self.stdout.write('Створення підрозділів...')

        # Бригада
        brigade = Unit.objects.create(name='24-та окрема механізована бригада імені короля Данила')

        # Батальйони
        battalion_1 = Unit.objects.create(name='1-й механізований батальйон', parent=brigade)
        battalion_2 = Unit.objects.create(name='2-й механізований батальйон', parent=brigade)
        battalion_3 = Unit.objects.create(name='3-й механізований батальйон', parent=brigade)
        tank_battalion = Unit.objects.create(name='Танковий батальйон', parent=brigade)
        artillery = Unit.objects.create(name='Артилерійський дивізіон', parent=brigade)
        support = Unit.objects.create(name='Батальйон забезпечення', parent=brigade)

        # Роти в 1-му батальйоні
        for i in range(1, 4):
            company = Unit.objects.create(name=f'{i}-та механізована рота', parent=battalion_1)
            # Взводи в роті
            for j in range(1, 4):
                platoon = Unit.objects.create(name=f'{j}-й механізований взвод', parent=company)
                # Відділення у взводі
                for k in range(1, 4):
                    Unit.objects.create(name=f'{k}-те відділення', parent=platoon)

        # Роти в 2-му батальйоні
        for i in range(1, 4):
            company = Unit.objects.create(name=f'{i + 3}-та механізована рота', parent=battalion_2)
            for j in range(1, 4):
                platoon = Unit.objects.create(name=f'{j}-й механізований взвод', parent=company)
                for k in range(1, 4):
                    Unit.objects.create(name=f'{k}-те відділення', parent=platoon)

        # Танкові роти
        for i in range(1, 3):
            Unit.objects.create(name=f'{i}-та танкова рота', parent=tank_battalion)

        # Артилерійські батареї
        for i in range(1, 4):
            Unit.objects.create(name=f'{i}-та гаубична батарея', parent=artillery)

        # Підрозділи забезпечення
        Unit.objects.create(name='Рота зв\'язку', parent=support)
        Unit.objects.create(name='Медична рота', parent=support)
        Unit.objects.create(name='Рота матеріально-технічного забезпечення', parent=support)
        Unit.objects.create(name='Інженерна рота', parent=support)
        Unit.objects.create(name='Розвідувальна рота', parent=brigade)

        self.stdout.write(f'Створено {Unit.objects.count()} підрозділів')

    def create_positions(self):
        """Створення штатних посад"""
        self.stdout.write('Створення штатних посад...')

        position_counter = 1

        # Командування бригади
        brigade = Unit.objects.get(name='24-та окрема механізована бригада імені короля Данила')
        positions_data = [
            (brigade, 'Командир бригади', 'Полковник', '100500', '24'),
            (brigade, 'Заступник командира бригади', 'Підполковник', '100500', '23'),
            (brigade, 'Начальник штабу', 'Підполковник', '900100', '23'),
            (brigade, 'Заступник начальника штабу', 'Майор', '900100', '22'),
        ]

        # Для кожного батальйону
        for battalion in Unit.objects.filter(name__contains='батальйон'):
            positions_data.extend([
                (battalion, 'Командир батальйону', 'Підполковник', '100500', '23'),
                (battalion, 'Заступник командира батальйону', 'Майор', '100400', '22'),
                (battalion, 'Начальник штабу батальйону', 'Майор', '900100', '22'),
            ])

        # Для кожної роти
        for company in Unit.objects.filter(name__contains='рота'):
            positions_data.extend([
                (company, 'Командир роти', 'Капітан', '100400', '21'),
                (company, 'Заступник командира роти', 'Старший лейтенант', '100400', '20'),
                (company, 'Старшина роти', 'Старший майстер-сержант', '100200', '15'),
            ])

        # Для кожного взводу
        for platoon in Unit.objects.filter(name__contains='взвод'):
            positions_data.extend([
                (platoon, 'Командир взводу', 'Лейтенант', '100300', '19'),
                (platoon, 'Заступник командира взводу', 'Старший сержант', '100200', '12'),
            ])

        # Для кожного відділення
        for squad in Unit.objects.filter(name__contains='відділення'):
            positions_data.extend([
                (squad, 'Командир відділення', 'Сержант', '100200', '10'),
                (squad, 'Старший стрілець', 'Молодший сержант', '100100', '8'),
                (squad, 'Кулеметник', 'Старший солдат', '100101', '6'),
                (squad, 'Гранатометник', 'Солдат', '100102', '5'),
                (squad, 'Стрілець', 'Солдат', '100100', '5'),
                (squad, 'Стрілець', 'Солдат', '100100', '5'),
                (squad, 'Стрілець-санітар', 'Солдат', '400100', '5'),
            ])

        # Створення посад
        for unit, position_name, category, specialty_code, tariff in positions_data:
            specialty = MilitarySpecialty.objects.get(code=specialty_code)
            Position.objects.create(
                unit=unit,
                position_index=f'П-{position_counter:05d}',
                name=position_name,
                category=category,
                specialty=specialty,
                tariff_rate=tariff
            )
            position_counter += 1

        self.stdout.write(f'Створено {Position.objects.count()} штатних посад')

    def create_servicemen(self):
        """Створення військовослужбовців"""
        self.stdout.write('Створення військовослужбовців...')

        # Українські прізвища, імена та по батькові
        last_names = [
            'Шевченко', 'Коваленко', 'Бондаренко', 'Ткаченко', 'Кравченко',
            'Олійник', 'Шевчук', 'Коваль', 'Поліщук', 'Бондар',
            'Ткачук', 'Мороз', 'Марченко', 'Лисенко', 'Руденко',
            'Савченко', 'Петренко', 'Кравчук', 'Мельник', 'Клименко',
            'Гончаренко', 'Василенко', 'Захаренко', 'Сидоренко', 'Павленко',
            'Романенко', 'Яковенко', 'Гриценко', 'Костенко', 'Левченко',
            'Тимошенко', 'Дорошенко', 'Кириченко', 'Федоренко', 'Бойко'
        ]

        first_names_male = [
            'Олександр', 'Михайло', 'Іван', 'Петро', 'Василь',
            'Андрій', 'Віктор', 'Сергій', 'Володимир', 'Микола',
            'Юрій', 'Олег', 'Дмитро', 'Максим', 'Артем',
            'Роман', 'Євген', 'Ігор', 'Богдан', 'Тарас',
            'Ярослав', 'Назар', 'Остап', 'Данило', 'Степан'
        ]

        middle_names_male = [
            'Олександрович', 'Михайлович', 'Іванович', 'Петрович', 'Васильович',
            'Андрійович', 'Вікторович', 'Сергійович', 'Володимирович', 'Миколайович',
            'Юрійович', 'Олегович', 'Дмитрович', 'Максимович', 'Артемович'
        ]

        cities = [
            'Київ', 'Харків', 'Одеса', 'Дніпро', 'Львів',
            'Запоріжжя', 'Кривий Ріг', 'Миколаїв', 'Вінниця', 'Херсон',
            'Полтава', 'Чернігів', 'Черкаси', 'Суми', 'Житомир',
            'Хмельницький', 'Рівне', 'Кропивницький', 'Івано-Франківськ', 'Тернопіль',
            'Луцьк', 'Ужгород', 'Чернівці'
        ]

        # Отримуємо посади та звання
        positions = list(Position.objects.all())
        ranks = {
            'Солдат': Rank.objects.get(name='Солдат'),
            'Старший солдат': Rank.objects.get(name='Старший солдат'),
            'Молодший сержант': Rank.objects.get(name='Молодший сержант'),
            'Сержант': Rank.objects.get(name='Сержант'),
            'Старший сержант': Rank.objects.get(name='Старший сержант'),
            'Головний сержант': Rank.objects.get(name='Головний сержант'),
            'Молодший лейтенант': Rank.objects.get(name='Молодший лейтенант'),
            'Лейтенант': Rank.objects.get(name='Лейтенант'),
            'Старший лейтенант': Rank.objects.get(name='Старший лейтенант'),
            'Капітан': Rank.objects.get(name='Капітан'),
            'Майор': Rank.objects.get(name='Майор'),
            'Підполковник': Rank.objects.get(name='Підполковник'),
            'Полковник': Rank.objects.get(name='Полковник'),
        }

        # Створюємо військовослужбовців для 70% посад
        filled_positions = random.sample(positions, k=int(len(positions) * 0.7))

        for i, position in enumerate(filled_positions):
            # Визначаємо звання за категорією посади
            if position.category in ranks:
                rank = ranks[position.category]
            else:
                rank = ranks['Солдат']

            # Генеруємо персональні дані
            birth_year = random.randint(1985, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)

            serviceman = Serviceman.objects.create(
                position=position,
                rank=rank,
                last_name=random.choice(last_names),
                first_name=random.choice(first_names_male),
                middle_name=random.choice(middle_names_male),
                date_of_birth=date(birth_year, birth_month, birth_day),
                place_of_birth=f'м. {random.choice(cities)}',
                tax_id_number=f'{random.randint(1000000000, 9999999999)}',
                passport_number=f'{random.choice(["АА", "АВ", "АС", "ВА", "ВВ", "ВС"])}{random.randint(100000, 999999)}'
            )

            # Прив'язуємо користувача для деяких військовослужбовців
            if i == 0:  # Командир бригади
                serviceman.user = User.objects.get(username='commander')
                serviceman.save()

        self.stdout.write(f'Створено {Serviceman.objects.count()} військовослужбовців')

    def create_contracts(self):
        """Створення контрактів"""
        self.stdout.write('Створення контрактів...')

        for serviceman in Serviceman.objects.all():
            # Визначаємо тривалість контракту за званням
            if serviceman.rank.order >= 11:  # Офіцери
                contract_years = 5
            else:  # Солдати та сержанти
                contract_years = 3

            # Дата початку контракту
            start_date = date.today() - timedelta(days=random.randint(30, 365 * 2))
            end_date = start_date + timedelta(days=365 * contract_years)

            Contract.objects.create(
                serviceman=serviceman,
                start_date=start_date,
                end_date=end_date,
                details=f'Контракт на {contract_years} років'
            )

        self.stdout.write(f'Створено {Contract.objects.count()} контрактів')

    def create_service_history(self):
        """Створення історії служби"""
        self.stdout.write('Створення історії служби...')

        # Для 30% військовослужбовців створюємо історію
        servicemen_with_history = random.sample(
            list(Serviceman.objects.all()),
            k=int(Serviceman.objects.count() * 0.3)
        )

        for serviceman in servicemen_with_history:
            # Призначення на посаду
            ServiceHistoryEvent.objects.create(
                serviceman=serviceman,
                event_type=ServiceHistoryEvent.EventType.APPOINTMENT,
                event_date=serviceman.contracts.first().start_date,
                details={
                    'position_id': serviceman.position.id if serviceman.position else None,
                    'position_name': str(serviceman.position) if serviceman.position else 'N/A'
                },
                order_reference=f'Наказ №{random.randint(1, 500)}/2024'
            )

            # Для деяких додаємо підвищення у званні
            if random.random() > 0.5:
                promotion_date = serviceman.contracts.first().start_date + timedelta(days=random.randint(180, 540))
                if promotion_date < date.today():
                    ServiceHistoryEvent.objects.create(
                        serviceman=serviceman,
                        event_type=ServiceHistoryEvent.EventType.PROMOTION,
                        event_date=promotion_date,
                        details={
                            'new_rank': serviceman.rank.name,
                            'previous_rank': 'Солдат'
                        },
                        order_reference=f'Наказ №{random.randint(501, 1000)}/2024'
                    )

        self.stdout.write(f'Створено {ServiceHistoryEvent.objects.count()} записів історії служби')

        # Виводимо підсумкову статистику
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('ПІДСУМКОВА СТАТИСТИКА:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Користувачів: {User.objects.count()}')
        self.stdout.write(f'Військових звань: {Rank.objects.count()}')
        self.stdout.write(f'ВОС: {MilitarySpecialty.objects.count()}')
        self.stdout.write(f'Підрозділів: {Unit.objects.count()}')
        self.stdout.write(f'Штатних посад: {Position.objects.count()}')
        self.stdout.write(f'Військовослужбовців: {Serviceman.objects.count()}')
        self.stdout.write(f'Контрактів: {Contract.objects.count()}')
        self.stdout.write(f'Записів історії: {ServiceHistoryEvent.objects.count()}')
        self.stdout.write('=' * 50)

        # Інформація про облікові записи
        self.stdout.write('\n' + self.style.WARNING('ОБЛІКОВІ ЗАПИСИ ДЛЯ ВХОДУ:'))
        self.stdout.write('Адміністратор: admin / admin123')
        self.stdout.write('Кадровий офіцер: hr_officer / hr123')
        self.stdout.write('Командир: commander / commander123')
        self.stdout.write('=' * 50)