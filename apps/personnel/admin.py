from django.contrib import admin
from .models import Rank, Serviceman, Contract, ServiceHistoryEvent

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 1

class ServiceHistoryEventInline(admin.TabularInline):
    model = ServiceHistoryEvent
    extra = 1
    readonly_fields = ('details', 'order_reference', 'event_type', 'event_date')

@admin.register(Serviceman)
class ServicemanAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rank', 'position')
    list_filter = ('rank', 'position__unit')
    search_fields = ('last_name', 'first_name', 'tax_id_number')
    autocomplete_fields = ('position', 'user')
    inlines = [ContractInline, ServiceHistoryEventInline]
    readonly_fields = ('user',)