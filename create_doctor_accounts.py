"""
Скрипт для создания учётных записей врачей в системе
Используется в управлении Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from django.contrib.auth.models import User
from doctors.models import Doctor

# Создание учётных записей для врачей
doctors_data = [
    {
        'email': 'petrov@medmi.ru',
        'password': 'Doctor123!',
        'first_name': 'Иван',
        'last_name': 'Петров'
    },
    {
        'email': 'smirnova@medmi.ru',
        'password': 'Doctor123!',
        'first_name': 'Мария',
        'last_name': 'Смирнова'
    },
    {
        'email': 'ivanov@medmi.ru',
        'password': 'Doctor123!',
        'first_name': 'Сергей',
        'last_name': 'Иванов'
    },
]

for doc_data in doctors_data:
    # Получаем врача по email
    doctor = Doctor.objects.filter(email=doc_data['email']).first()
    
    if doctor and not doctor.user:
        # Создаём пользователя
        username = doc_data['email'].split('@')[0]
        try:
            user = User.objects.create_user(
                username=username,
                email=doc_data['email'],
                password=doc_data['password'],
                first_name=doc_data['first_name'],
                last_name=doc_data['last_name']
            )
            
            # Связываем врача с пользователем
            doctor.user = user
            doctor.save()
            
            print(f"✓ Создана учётная запись для Dr. {doctor.first_name} {doctor.last_name}")
            print(f"  Логин: {username}")
            print(f"  Email: {doc_data['email']}")
            print(f"  Пароль: {doc_data['password']}")
            print()
        except Exception as e:
            print(f"✗ Ошибка при создании учётной записи для {doc_data['email']}: {e}")
    else:
        if not doctor:
            print(f"✗ Врач с email {doc_data['email']} не найден в базе")
        else:
            print(f"⚠ Врач {doctor.first_name} {doctor.last_name} уже имеет учётную запись")

print("\nГотово! Врачи могут теперь входить в систему.")
