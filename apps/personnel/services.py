from django.db import transaction
from .models import Serviceman, ServiceHistoryEvent
from apps.staffing.models import Position
from datetime import date

@transaction.atomic
def transfer_serviceman(serviceman: Serviceman, new_position: Position, order_reference: str, event_date: date):
    """
    Виконує повний процес переведення військовослужбовця на нову посаду.
    Ця функція є прикладом реалізації бізнес-логіки в сервісному шарі.
    """
    old_position = serviceman.position

    # Перевіряємо, чи нова посада не зайнята
    if hasattr(new_position, 'serviceman') and new_position.serviceman is not None:
         raise ValueError(f"Посада {new_position} вже зайнята.")

    # Призначаємо нову посаду
    serviceman.position = new_position
    serviceman.save()

    # Створюємо запис в історії служби
    ServiceHistoryEvent.objects.create(
        serviceman=serviceman,
        event_type=ServiceHistoryEvent.EventType.TRANSFER,
        event_date=event_date,
        details={
            'from_position_id': old_position.id if old_position else None,
            'from_position_name': str(old_position) if old_position else 'N/A',
            'to_position_id': new_position.id,
            'to_position_name': str(new_position),
        },
        order_reference=order_reference
    )

    # Тут може бути додаткова логіка, напр. відправка сповіщень
    print(f"Військовослужбовця {serviceman} переведено на посаду {new_position}.")

    return serviceman