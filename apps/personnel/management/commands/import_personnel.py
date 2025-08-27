# apps/personnel/management/commands/import_personnel.py
"""
Management command для імпорту даних військовослужбовців з CSV файлу
Використання: python manage.py import_personnel path/to/file.csv
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.personnel.models import Serviceman, Rank
from apps.staffing.models import Position
import csv
from datetime import datetime


class Command(BaseCommand):
    help = 'Імпорт даних військовослужбовців з CSV файлу'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Шлях до CSV файлу з даними'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Оновити існуючі записи замість пропуску'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тестовий запуск без збереження даних'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options.get('update', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 ТЕСТОВИЙ РЕЖИМ - дані не будуть збережені'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_count = 0

                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):  # Починаємо з 2 (1 - заголовки)
                        try:
                            # Обробка даних
                            result = self.process_row(row, update_existing)

                            if result == 'created':
                                created_count += 1
                                self.stdout.write(
                                    f'✅ Рядок {row_num}: Створено {row.get("Прізвище")} {row.get("Ім\'я")}')
                            elif result == 'updated':
                                updated_count += 1
                                self.stdout.write(
                                    f'🔄 Рядок {row_num}: Оновлено {row.get("Прізвище")} {row.get("Ім\'я")}')
                            elif result == 'skipped':
                                skipped_count += 1
                                self.stdout.write(f'⏭️ Рядок {row_num}: Пропущено (вже існує)')

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(f'❌ Рядок {row_num}: Помилка - {str(e)}')
                            )

                    if dry_run:
                        transaction.set_rollback(True)
                        self.stdout.write(self.style.WARNING('\n🔙 Відкат транзакції (тестовий режим)'))

                # Виводимо статистику
                self.stdout.write('\n' + '=' * 50)
                self.stdout.write('📊 РЕЗУЛЬТАТИ ІМПОРТУ:')
                self.stdout.write('=' * 50)
                self.stdout.write(self.style.SUCCESS(f'✅ Створено: {created_count}'))
                self.stdout.write(self.style.WARNING(f'🔄 Оновлено: {updated_count}'))
                self.stdout.write(f'⏭️ Пропущено: {skipped_count}')
                self.stdout.write(self.style.ERROR(f'❌ Помилок: {error_count}'))
                self.stdout.write('=' * 50)

                if not dry_run and (created_count > 0 or updated_count > 0):
                    self.stdout.write(self.style.SUCCESS('✅ Імпорт завершено успішно!'))

        except FileNotFoundError:
            raise CommandError(f'Файл {csv_file} не знайдено')
        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу: {str(e)}')

    def process_row(self, row, update_existing):
        """Обробка одного рядка з CSV"""
        # Очищаємо пробіли з ключів та значень
        row = {k.strip(): v.strip() for k, v in row.items()}

        # Обов'язкові поля
        required_fields = ['Прізвище', "Ім'я", 'РНОКПП', 'Дата народження', 'Звання']
        for field in required_fields:
            if not row.get(field):
                raise ValueError(f"Відсутнє обов'язкове поле: {field}")

        # Парсимо дату народження
        try:
            date_of_birth = datetime.strptime(row['Дата народження'], '%d.%m.%Y').date()
        except ValueError:
            raise ValueError(f"Неправильний формат дати народження: {row['Дата народження']}")

        # Знаходимо звання
        try:
            rank = Rank.objects.get(name=row['Звання'])
        except Rank.DoesNotExist:
            raise ValueError(f"Звання '{row['Звання']}' не знайдено")

        # Знаходимо посаду якщо вказана
        position = None
        if row.get('Індекс посади'):
            try:
                position = Position.objects.get(position_index=row['Індекс посади'])
            except Position.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Посада з індексом '{row['Індекс посади']}' не знайдена")
                )

        # Перевіряємо чи існує військовослужбовець
        serviceman = None
        if row.get('РНОКПП'):
            serviceman = Serviceman.objects.filter(tax_id_number=row['РНОКПП']).first()

        if serviceman:
            if update_existing:
                # Оновлюємо існуючий запис
                serviceman.last_name = row['Прізвище']
                serviceman.first_name = row["Ім'я"]
                serviceman.middle_name = row.get('По батькові', '')
                serviceman.date_of_birth = date_of_birth
                serviceman.place_of_birth = row.get('Місце народження', '')
                serviceman.passport_number = row.get('Паспорт', '')
                serviceman.rank = rank
                if position:
                    serviceman.position = position
                serviceman.save()
                return 'updated'
            else:
                return 'skipped'
        else:
            # Створюємо новий запис
            Serviceman.objects.create(
                last_name=row['Прізвище'],
                first_name=row["Ім'я"],
                middle_name=row.get('По батькові', ''),
                date_of_birth=date_of_birth,
                place_of_birth=row.get('Місце народження', ''),
                tax_id_number=row.get('РНОКПП'),
                passport_number=row.get('Паспорт', ''),
                rank=rank,
                position=position
            )
            return 'created'


# Приклад CSV файлу:
"""
Прізвище,Ім'я,По батькові,Дата народження,Місце народження,РНОКПП,Паспорт,Звання,Індекс посади
Шевченко,Олександр,Іванович,15.03.1990,м. Київ,3012345678,АА123456,Капітан,П-00001
Коваленко,Петро,Васильович,22.07.1985,м. Харків,2987654321,ВВ654321,Майор,П-00002
"""