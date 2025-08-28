# apps/documents/admin.py
from django.contrib import admin
from .models import ServicemanReport


@admin.register(ServicemanReport)
class ServicemanReportAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для моделі рапортів.
    """
    list_display = (
        'registration_number',
        'author',
        'report_type',
        'submission_date',
        'status',
        'recipient_position'
    )
    list_filter = ('status', 'report_type', 'submission_date')
    search_fields = (
        'registration_number',
        'summary',
        'author__last_name',
        'author__first_name'
    )

    # Використовуємо autocomplete для зручного пошуку військовослужбовця
    autocomplete_fields = ['author']

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основна інформація', {
            'fields': ('registration_number', 'submission_date', 'report_type', 'status')
        }),
        ('Сторони рапорту', {
            'fields': ('author', 'recipient_position')
        }),
        ('Зміст та резолюція', {
            'fields': ('summary', 'full_text', 'resolution', 'reviewed_by')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        При збереженні моделі через адмін-панель,
        якщо було додано резолюцію, автоматично заповнюємо поле 'reviewed_by'.
        """
        if 'resolution' in form.changed_data and obj.resolution:
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)