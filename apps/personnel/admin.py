from django.contrib import admin
from .models import Rank, Serviceman, Contract, ServiceHistoryEvent, Education, FamilyMember


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


class ContractInline(admin.TabularInline):
    """Дозволяє редагувати контракти на сторінці військовослужбовця."""
    model = Contract
    extra = 1
    classes = ['collapse']  # Робить блок згорнутим за замовчуванням


class EducationInline(admin.TabularInline):
    """Дозволяє редагувати освіту на сторінці військовослужбовця (нова)."""
    model = Education
    extra = 1
    classes = ['collapse']


class FamilyMemberInline(admin.TabularInline):
    """Дозволяє редагувати членів сім'ї на сторінці військовослужбовця (нова)."""
    model = FamilyMember
    extra = 1
    classes = ['collapse']


class ServiceHistoryEventInline(admin.TabularInline):
    """Дозволяє переглядати історію служби на сторінці військовослужбовця."""
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

    # Додаємо нові інлайни для освіти та сім'ї
    inlines = [EducationInline, FamilyMemberInline, ContractInline, ServiceHistoryEventInline]

    readonly_fields = ('user',)  # Обліковий запис не редагується напряму

    # Оновлюємо fieldsets для групування полів
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