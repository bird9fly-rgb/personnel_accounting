# apps/personnel/management/commands/import_personnel.py
"""
Management command для імпорту даних військовослужбовців з CSV файлу.
Використання: python manage.py import_personnel /шлях/до/файлу.csv
"""
import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.personnel.models import Serviceman, Rank, Education, FamilyMember
from apps.staffing.models import Position


class Command(BaseCommand):
    help = 'Імпортує дані військовослужбовців з CSV файлу, що відповідає структурі Електронного журналу'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Шлях до CSV файлу з даними (аркуш "2. ООС")')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Оновити існуючі записи, якщо знайдено військовослужбовця за РНОКПП.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тестовий запуск без збереження даних до БД.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['csv_file']
        update_existing = options['update']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS(f'Починаю імпорт з файлу: {file_path}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ ТЕСТОВОГО ЗАПУСКУ: Зміни не буде збережено.'))

        # Словники для кешування, щоб уникнути повторних запитів до БД
        ranks_cache = {rank.name: rank for rank in Rank.objects.all()}
        positions_cache = {pos.position_index: pos for pos in Position.objects.all()}

        processed_count = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Пропускаємо перші 3 рядки заголовку, як у вашому файлі
                for _ in range(3):
                    next(file)

                reader = csv.DictReader(file)
                for row in reader:
                    processed_count += 1
                    tax_id = row.get('РНОКПП  (за наявності)')
                    if not tax_id:
                        self.stdout.write(
                            self.style.ERROR(f'Рядок {processed_count + 3}: Пропущено - відсутній РНОКПП.'))
                        error_count += 1
                        continue

                    try:
                        serviceman = Serviceman.objects.filter(tax_id_number=tax_id).first()

                        if serviceman and not update_existing:
                            skipped_count += 1
                            continue

                        # Розбір ПІБ
                        full_name = row['ПРІЗВИЩЕ (за наявності) Ім\'я По батькові (за наявності)'].split()
                        last_name = full_name[0]
                        first_name = full_name[1] if len(full_name) > 1 else ''
                        middle_name = ' '.join(full_name[2:])

                        # Отримання пов'язаних об'єктів з кешу
                        rank = ranks_cache.get(row['Звання'])
                        position_index = row['Індекс посади /\\nІндексм посад, які обіймав(ла)'].split('\\n')[0]
                        position = positions_cache.get(position_index)

                        if not rank:
                            raise ValueError(f"Звання '{row['Звання']}' не знайдено у довіднику.")

                        # Створення або оновлення об'єкта
                        defaults = {
                            'rank': rank,
                            'last_name': last_name,
                            'first_name': first_name,
                            'middle_name': middle_name,
                            'date_of_birth': datetime.strptime(row['Дата народження'], '%Y-%m-%d').date(),
                            'place_of_birth': row['Місце народження'],
                            'passport_number': row[
                                'Серія (за наявності) і номер документа, що посвідчує особу та назва документа'],
                            'personal_number': tax_id,
                            'enlistment_date': datetime.strptime(
                                row['Ким і коли призваний (прийнятий) на військову службу'].split(',')[-1].strip(),
                                '%Y-%m-%d').date(),
                            'enlistment_authority': ','.join(
                                row['Ким і коли призваний (прийнятий) на військову службу'].split(',')[:-1]),
                            'position': position,
                        }

                        if serviceman:
                            # Оновлення
                            for key, value in defaults.items():
                                setattr(serviceman, key, value)
                            serviceman.save()
                            updated_count += 1
                        else:
                            # Створення
                            Serviceman.objects.create(tax_id_number=tax_id, **defaults)
                            created_count += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Рядок {processed_count + 3}: Помилка - {e}'))
                        error_count += 1

        except FileNotFoundError:
            raise CommandError(f'Файл не знайдено: {file_path}')
        except Exception as e:
            raise CommandError(f'Загальна помилка обробки файлу: {e}')

        if dry_run:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING('Відкат транзакції. Жодних змін не було внесено.'))

        self.stdout.write(self.style.SUCCESS('----- РЕЗУЛЬТАТИ ІМПОРТУ -----'))
        self.stdout.write(f'Оброблено рядків: {processed_count}')
        self.stdout.write(f'Створено нових записів: {created_count}')
        self.stdout.write(f'Оновлено існуючих записів: {updated_count}')
        self.stdout.write(f'Пропущено (дублікати): {skipped_count}')
        self.stdout.write(self.style.ERROR(f'Помилок: {error_count}'))