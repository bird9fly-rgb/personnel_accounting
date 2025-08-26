from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Unit, MilitarySpecialty, Position

@admin.register(Unit)
class UnitAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title')
    list_display_links = ('indented_title',)
    search_fields = ('name',)

@admin.register(MilitarySpecialty)
class MilitarySpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'position_index', 'category', 'specialty')
    list_filter = ('unit', 'specialty', 'category')
    search_fields = ('name', 'position_index', 'unit__name')
    autocomplete_fields = ('unit', 'specialty')