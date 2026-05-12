from django.contrib import admin
from .models import Clinic

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'working_hours')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Адрес и координаты', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Время работы', {
            'fields': ('working_hours',)
        }),
    )
