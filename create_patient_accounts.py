"""
Скрипт для создания учётных записей пациентов в системе
Используется в управлении Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from django.contrib.auth.models import User
from patients.models import Patient

# Создание учётных записей для пациентов (демо)
patients_data = [
    {
        'email': 'patient1@example.com',
        'password': 'Patient123!',
        'first_name': 'Александр',
        'last_name': 'Иванов'
    },
    {
        'email': 'patient2@example.com',
        'password': 'Patient123!',
        'first_name': 'Елена',
        'last_name': 'Петрова'
    },
    {
        'email': 'patient3@example.com',
        'password': 'Patient123!',
        'first_name': 'Дмитрий',
        'last_name': 'Сидоров'
    },
]

for pat_data in patients_data:
    # Получаем пациента по email
    patient = Patient.objects.filter(email=pat_data['email']).first()
    
    if patient and not patient.user:
        # Создаём пользователя
        username = pat_data['email'].split('@')[0]
        try:
            user = User.objects.create_user(
                username=username,
                email=pat_data['email'],
                password=pat_data['password'],
                first_name=pat_data['first_name'],
                last_name=pat_data['last_name']
            )
            
            # Связываем пациента с пользователем
            patient.user = user
            patient.save()
            
            print(f"✓ Создана учётная запись для пациента {patient.first_name} {patient.last_name}")
            print(f"  Логин: {username}")
            print(f"  Email: {pat_data['email']}")
            print(f"  Пароль: {pat_data['password']}")
            print()
        except Exception as e:
            print(f"✗ Ошибка при создании учётной записи для {pat_data['email']}: {e}")
    else:
        if not patient:
            print(f"⚠ Пациент с email {pat_data['email']} не найден в базе, создаём нового...")
            
            # Если пациента нет, создаём его
            try:
                username = pat_data['email'].split('@')[0]
                user = User.objects.create_user(
                    username=username,
                    email=pat_data['email'],
                    password=pat_data['password'],
                    first_name=pat_data['first_name'],
                    last_name=pat_data['last_name']
                )
                
                # Создаём минимального пациента
                from datetime import date
                patient = Patient.objects.create(
                    user=user,
                    first_name=pat_data['first_name'],
                    last_name=pat_data['last_name'],
                    date_of_birth=date(1990, 1, 1),
                    gender='M',
                    phone='123-456-7890',
                    email=pat_data['email'],
                    address='Бишкек'
                )
                
                print(f"✓ Создан новый пациент {patient.first_name} {patient.last_name}")
                print(f"  Логин: {username}")
                print(f"  Пароль: {pat_data['password']}")
                print()
            except Exception as e:
                print(f"✗ Ошибка при создании пациента: {e}")
        else:
            print(f"⚠ Пациент {patient.first_name} {patient.last_name} уже имеет учётную запись")

print("\nГотово! Пациенты могут теперь входить в систему.")
