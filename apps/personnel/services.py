# apps/personnel/services.py
from django.db import transaction
from .models import Serviceman, ServiceHistoryEvent, PositionHistory  # <-- Додайте імпорт PositionHistory
from apps.staffing.models import Position
from datetime import date


@transaction.atomic
def transfer_serviceman(serviceman: Serviceman, new_position: Position, order_reference: str, event_date: date,
                        event_type: str):
    """
    Виконує повний процес переведення або первинного призначення військовослужбовця.
    """
    old_position = serviceman.position

    # Оновлюємо запис в історії посад для старої посади (якщо вона була)
    if old_position:
        PositionHistory.objects.filter(
            serviceman=serviceman,
            position=old_position,
            end_date__isnull=True
        ).update(end_date=event_date)

        old_position.serviceman = None
        old_position.save()

    if hasattr(new_position, 'serviceman') and new_position.serviceman is not None:
        raise ValueError(f"Посада '{new_position}' вже зайнята військовослужбовцем {new_position.serviceman}.")

    serviceman.position = new_position
    serviceman.save()

    # Створюємо новий запис в історії посад для нової посади
    PositionHistory.objects.create(
        serviceman=serviceman,
        position=new_position,
        start_date=event_date,
        order_reference=order_reference
    )

    # Створюємо загальний запис в історії служби (як і раніше)
    ServiceHistoryEvent.objects.create(
        serviceman=serviceman,
        event_type=event_type,
        event_date=event_date,
        details={
            'from_position_id': old_position.id if old_position else None,
            'from_position_name': str(old_position) if old_position else 'Не було',
            'to_position_id': new_position.id,
            'to_position_name': str(new_position),
        },
        order_reference=order_reference
    )

    print(f"Військовослужбовця {serviceman} призначено/переведено на посаду {new_position}.")
    return serviceman