from django.contrib import admin
from .models import Doctor, Review, DoctorBooking

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'specialization', 'phone', 'email', 'is_featured', 'start_time', 'end_time')
    list_filter = ('specialization', 'is_featured')
    search_fields = ('user__username', 'first_name', 'last_name', 'specialization')
    fieldsets = (
        ('Аккаунт врача', {
            'fields': ('user',)
        }),
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'specialization', 'license_number')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Местоположение', {
            'fields': ('address', 'latitude', 'longitude'),
            'description': 'Адрес кабинета и координаты для отображения на карте'
        }),
        ('Расписание работы', {
            'fields': ('start_time', 'end_time', 'appointment_duration'),
            'description': 'Установите время работы и длительность приёма в минутах'
        }),
        ('Фото и Статус', {
            'fields': ('photo_url', 'is_featured')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'rating', 'created_at', 'is_verified')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('patient_name', 'patient_email', 'comment')
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('doctor', 'patient_name', 'patient_email', 'rating')
        }),
        ('Содержание', {
            'fields': ('comment',)
        }),
        ('Статус', {
            'fields': ('is_verified', 'created_at'),
            'description': 'Отзыв появится на сайте только если отмечен как проверенный'
        }),
    )
    readonly_fields = ('created_at',)


@admin.register(DoctorBooking)
class DoctorBookingAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient_name', 'patient_email', 'patient_phone')
    fieldsets = (
        ('Информация о пациенте', {
            'fields': ('patient_name', 'patient_email', 'patient_phone')
        }),
        ('Запись на прием', {
            'fields': ('doctor', 'appointment_date', 'reason')
        }),
        ('Статус', {
            'fields': ('status', 'notes')
        }),
        ('История', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)


