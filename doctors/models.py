from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    license_number = models.CharField(max_length=50, unique=True)
    photo_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Рабочие часы
    start_time = models.TimeField(default="09:00", help_text="Время начала приёма")
    end_time = models.TimeField(default="18:00", help_text="Время окончания приёма")
    appointment_duration = models.IntegerField(default=30, help_text="Длительность приёма в минутах")

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum([r.rating for r in reviews]) / len(reviews), 1)
        return 0

    def get_reviews_count(self):
        return self.reviews.count()

    def get_available_slots(self, date):
        """Получить доступные слоты для конкретной даты (по часам)"""
        from datetime import datetime as dt, timedelta
        
        slots = []
        current_time = dt.combine(date, self.start_time)
        end_datetime = dt.combine(date, self.end_time)
        
        while current_time < end_datetime:
            # Проверяем, есть ли уже запись в этот час
            existing_booking = DoctorBooking.objects.filter(
                doctor=self,
                appointment_date__date=date,
                appointment_date__hour=current_time.hour,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if not existing_booking:
                slots.append({
                    'time': current_time.time(),
                    'datetime': current_time,
                    'available': True
                })
            
            # Переходим к следующему часу
            current_time = current_time + timedelta(hours=1)
        
        return slots


class Review(models.Model):
    RATING_CHOICES = [
        (5, '⭐⭐⭐⭐⭐ Отлично'),
        (4, '⭐⭐⭐⭐ Хорошо'),
        (3, '⭐⭐⭐ Нормально'),
        (2, '⭐⭐ Плохо'),
        (1, '⭐ Очень плохо'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.patient_name} для {self.doctor}"


class DoctorBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=15)
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date']
        unique_together = ['doctor', 'appointment_date', 'status']

    def __str__(self):
        return f"Запись: {self.patient_name} - Dr. {self.doctor} ({self.appointment_date.strftime('%d.%m.%Y %H:%M')})"
