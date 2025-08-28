# apps/orders/services.py
from django.db import transaction
from django.utils import timezone

from .models import Order, OrderAction
from apps.personnel.models import Serviceman, Rank, ServiceHistoryEvent
from apps.staffing.models import Position


class OrderExecutionError(Exception):
    """Спеціальний клас виключень для помилок під час виконання наказу."""
    pass


@transaction.atomic
def execute_order(order: Order, executing_user):
    """
    Виконує наказ та всі пов'язані з ним дії.
    Змінює статус наказу на 'Виконано'.
    """
    if order.status not in [Order.OrderStatus.SIGNED, Order.OrderStatus.ON_APPROVAL]:
        raise OrderExecutionError(
            f"Наказ №{order.order_number} не може бути виконаний, оскільки має статус '{order.get_status_display()}'.")

    for action in order.actions.filter(execution_status=False):
        serviceman = action.personnel
        details = action.details

        if action.action_type in [OrderAction.ActionType.APPOINT, OrderAction.ActionType.TRANSFER]:
            new_position_id = details.get('new_position_id')
            if not new_position_id:
                raise OrderExecutionError(f"Для дії '{action.get_action_type_display()}' не вказано ID нової посади.")

            try:
                new_position = Position.objects.get(pk=new_position_id)
            except Position.DoesNotExist:
                raise OrderExecutionError(f"Посада з ID={new_position_id} не знайдена.")

            from apps.personnel.services import transfer_serviceman

            # Визначаємо тип події для історії
            event_type_map = {
                OrderAction.ActionType.APPOINT: ServiceHistoryEvent.EventType.APPOINTMENT,
                OrderAction.ActionType.TRANSFER: ServiceHistoryEvent.EventType.TRANSFER,
            }

            transfer_serviceman(
                serviceman=serviceman,
                new_position=new_position,
                order_reference=str(order),
                event_date=order.order_date,
                event_type=event_type_map[action.action_type]  # <-- Передаємо правильний тип події
            )

        elif action.action_type == OrderAction.ActionType.PROMOTE:
            new_rank_id = details.get('new_rank_id')
            if not new_rank_id:
                raise OrderExecutionError(f"Для дії '{action.get_action_type_display()}' не вказано ID нового звання.")

            try:
                new_rank = Rank.objects.get(pk=new_rank_id)
            except Rank.DoesNotExist:
                raise OrderExecutionError(f"Звання з ID={new_rank_id} не знайдено.")

            previous_rank_name = serviceman.rank.name
            serviceman.rank = new_rank
            serviceman.save()

            ServiceHistoryEvent.objects.create(
                serviceman=serviceman,
                event_type=ServiceHistoryEvent.EventType.PROMOTION,
                event_date=order.order_date,
                details={'previous_rank': previous_rank_name, 'new_rank': new_rank.name},
                order_reference=str(order)
            )

        elif action.action_type == OrderAction.ActionType.DISMISS:
            serviceman.status = Serviceman.Status.DISMISSED
            if serviceman.position:
                old_position = serviceman.position
                serviceman.position = None
                old_position.serviceman = None
                old_position.save()
            serviceman.save()

            ServiceHistoryEvent.objects.create(
                serviceman=serviceman,
                event_type=ServiceHistoryEvent.EventType.DISMISSAL,
                event_date=order.order_date,
                details={'reason': details.get('reason', 'Звільнення зі служби')},
                order_reference=str(order)
            )

        action.execution_status = True
        action.save()

    order.status = Order.OrderStatus.EXECUTED
    order.save()

    print(f"Користувач {executing_user} виконав наказ №{order.order_number}")

    return order