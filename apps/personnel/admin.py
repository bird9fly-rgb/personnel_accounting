from django.contrib import admin
from .models import (
    Rank, Serviceman, Contract, ServiceHistoryEvent,
    Education, FamilyMember, TemporaryArrival, IrrecoverableLoss
)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 1
    classes = ['collapse']


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    classes = ['collapse']


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    classes = ['collapse']


class ServiceHistoryEventInline(admin.TabularInline):
    model = ServiceHistoryEvent
    extra = 0
    readonly_fields = ('event_type', 'event_date', 'details', 'order_reference')
    can_delete = False
    classes = ['collapse']


@admin.register(Serviceman)
class ServicemanAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'personal_number', 'rank', 'position', 'status')
    list_filter = ('status', 'rank', 'position__unit')
    search_fields = ('last_name', 'first_name', 'personal_number', 'tax_id_number')
    autocomplete_fields = ('position', 'user')

    inlines = [EducationInline, FamilyMemberInline, ContractInline, ServiceHistoryEventInline]

    readonly_fields = ('user',)

    fieldsets = (
        ('Основна інформація', {
            'fields': ('last_name', 'first_name', 'middle_name', 'photo')
        }),
        ('Службові дані', {
            'fields': ('status', 'rank', 'position', 'personal_number')
        }),
        ('Ідентифікаційні дані', {
            'fields': ('date_of_birth', 'place_of_birth', 'tax_id_number', 'passport_number')
        }),
        ('Дані про призов', {
            'fields': ('enlistment_date', 'enlistment_authority'),
            'classes': ('collapse',)
        }),
        ('Системна інформація', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TemporaryArrival)
class TemporaryArrivalAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rank_name', 'origin_unit', 'arrival_date', 'departure_date')
    list_filter = ('arrival_date', 'origin_unit')
    search_fields = ('full_name', 'origin_unit', 'arrival_reason')
    fieldsets = (
        (None, {
            'fields': ('full_name', 'rank_name', 'position_name')
        }),
        ('Інформація про переміщення', {
            'fields': (
            'origin_unit', 'arrival_reason', 'arrival_date', 'arrival_order', 'departure_date', 'departure_order')
        }),
        ('Додатково', {
            'fields': ('notes',)
        }),
    )


# НОВИЙ КЛАС для вкладки "7. Безповоротні втрати"
@admin.register(IrrecoverableLoss)
class IrrecoverableLossAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для моделі безповоротних втрат.
    """
    list_display = ('serviceman', 'loss_type', 'loss_date', 'loss_location')
    list_filter = ('loss_type', 'loss_date')
    search_fields = ('serviceman__last_name', 'serviceman__first_name', 'loss_location', 'circumstances')
    autocomplete_fields = ['serviceman']

    fieldsets = (
        (None, {
            'fields': ('serviceman', 'loss_type', 'loss_date')
        }),
        ('Деталі інциденту', {
            'fields': ('circumstances', 'loss_location', 'burial_location')
        }),
        ('Облікова інформація', {
            'fields': ('exclusion_date', 'exclusion_order', 'notification_details')
        }),
    )