# apps/orders/admin.py
from django.contrib import admin, messages
from .models import Order, OrderAction
from .services import execute_order, OrderExecutionError


class OrderActionInline(admin.TabularInline):
    """
    Дозволяє редагувати дії безпосередньо на сторінці наказу.
    """
    model = OrderAction
    extra = 1  # Кількість порожніх форм для додавання
    autocomplete_fields = ['personnel']
    raw_id_fields = ('personnel',) # Використовуйте, якщо багато військовослужбовців

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date', 'order_type', 'status', 'issuing_authority', 'created_by')
    list_filter = ('status', 'order_type', 'order_date')
    search_fields = ('order_number', 'order_text', 'issuing_authority')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderActionInline]
    actions = ['execute_selected_orders']
    fieldsets = (
        (None, {
            'fields': ('order_number', 'order_date', 'order_type', 'status')
        }),
        ('Деталі наказу', {
            'fields': ('issuing_authority', 'order_text')
        }),
        ('Системна інформація', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Виконати вибрані накази")
    def execute_selected_orders(self, request, queryset):
        """
        Адмін-дія для масового виконання наказів.
        """
        executed_count = 0
        for order in queryset:
            try:
                execute_order(order, request.user)
                executed_count += 1
            except OrderExecutionError as e:
                self.message_user(request, f"Помилка виконання наказу №{order.order_number}: {e}", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Невідома помилка при виконанні наказу №{order.order_number}: {e}",
                                  level=messages.ERROR)

        if executed_count > 0:
            self.message_user(request, f"Успішно виконано {executed_count} наказ(ів).", level=messages.SUCCESS)


@admin.register(OrderAction)
class OrderActionAdmin(admin.ModelAdmin):
    list_display = ('order', 'personnel', 'action_type', 'execution_status')
    list_filter = ('action_type', 'execution_status', 'order__order_date')
    search_fields = ('personnel__last_name', 'personnel__first_name', 'order__order_number')
    autocomplete_fields = ['order', 'personnel']
    raw_id_fields = ('order', 'personnel')