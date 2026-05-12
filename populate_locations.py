import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from locations.models import Clinic
from doctors.models import Doctor

# Удаляем старые клиники
Clinic.objects.all().delete()

# Добавляем клинику Медми в Бишкеке
clinic = Clinic.objects.create(
    name='Медми - Клиника здоровья',
    address='пр. Май, 116, Бишкек, Кыргызстан',
    phone='+996-312-123-45-67',
    email='info@medmi.kg',
    latitude=42.8746,
    longitude=74.5698,
    description='Современная медицинская клиника с опытными специалистами и современным оборудованием в центре Бишкека.',
    working_hours='9:00 - 18:00, пн-пт; 10:00 - 16:00, сб'
)
print(f"Клиника добавлена: {clinic.name}")

# Обновляем врачей с адресами и координатами в Бишкеке
doctors_locations = [
    {
        'id': 1,
        'address': 'Кабинет 101, 1 этаж, Медми Бишкек',
        'latitude': 42.8746,
        'longitude': 74.5698
    },
    {
        'id': 2,
        'address': 'Кабинет 202, 2 этаж, Медми Бишкек',
        'latitude': 42.8752,
        'longitude': 74.5705
    },
    {
        'id': 3,
        'address': 'Кабинет 301, 3 этаж, Медми Бишкек',
        'latitude': 42.8740,
        'longitude': 74.5691
    },
]

for doc_info in doctors_locations:
    try:
        doctor = Doctor.objects.get(id=doc_info['id'])
        doctor.address = doc_info['address']
        doctor.latitude = doc_info['latitude']
        doctor.longitude = doc_info['longitude']
        doctor.save()
        print(f"Врач обновлен: {doctor.first_name} {doctor.last_name} - {doctor.address}")
    except Doctor.DoesNotExist:
        pass

print("Данные геолокации в Бишкеке добавлены успешно!")

