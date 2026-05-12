import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from doctors.models import Doctor

# Удаляем старых врачей
Doctor.objects.all().delete()

# Добавляем новых врачей с фото
doctors_data = [
    {
        'first_name': 'Иван',
        'last_name': 'Петров',
        'specialization': 'Кардиолог',
        'phone': '+7-900-123-45-67',
        'email': 'petrov@medmi.ru',
        'license_number': 'LIC001',
        'photo_url': 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&h=300&fit=crop',
        'is_featured': True
    },
    {
        'first_name': 'Мария',
        'last_name': 'Смирнова',
        'specialization': 'Терапевт',
        'phone': '+7-900-234-56-78',
        'email': 'smirnova@medmi.ru',
        'license_number': 'LIC002',
        'photo_url': 'https://images.unsplash.com/photo-1559839734335-e757de900ba1?w=400&h=300&fit=crop',
        'is_featured': True
    },
    {
        'first_name': 'Сергей',
        'last_name': 'Иванов',
        'specialization': 'Невролог',
        'phone': '+7-900-345-67-89',
        'email': 'ivanov@medmi.ru',
        'license_number': 'LIC003',
        'photo_url': 'https://images.unsplash.com/photo-1612671776877-63dd8c32c6e1?w=400&h=300&fit=crop',
        'is_featured': False
    },
]

for doctor_data in doctors_data:
    Doctor.objects.create(**doctor_data)
    print(f"Добавлен врач: {doctor_data['first_name']} {doctor_data['last_name']}")

print(f"Всего врачей добавлено: {Doctor.objects.count()}")
