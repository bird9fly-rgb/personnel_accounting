from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('middle_name',)}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']