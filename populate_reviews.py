import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from doctors.models import Doctor, Review

# Добавляем пример отзывов для врачей
review_data = [
    {
        'doctor_id': 1,
        'patient_name': 'Алексей Шахов',
        'patient_email': 'alexey@example.com',
        'rating': 5,
        'comment': 'Отличный врач! Очень внимательный и профессиональный. Рекомендую всем!',
        'is_verified': True
    },
    {
        'doctor_id': 1,
        'patient_name': 'Мария Иванова',
        'patient_email': 'maria@example.com',
        'rating': 4,
        'comment': 'Хороший врач, быстро помог. Единственное - очереди большие.',
        'is_verified': True
    },
    {
        'doctor_id': 2,
        'patient_name': 'Сергей Петров',
        'patient_email': 'sergey@example.com',
        'rating': 5,
        'comment': 'Dr. Смирнова - просто волшебница! Чувствую себя намного лучше после приема.',
        'is_verified': True
    },
    {
        'doctor_id': 2,
        'patient_name': 'Анна Сидорова',
        'patient_email': 'anna@example.com',
        'rating': 5,
        'comment': 'Очень добрая и внимательная врач. Рекомендую!',
        'is_verified': True
    },
    {
        'doctor_id': 3,
        'patient_name': 'Иван Федоров',
        'patient_email': 'ivan@example.com',
        'rating': 4,
        'comment': 'Компетентный врач. Помог разобраться с проблемой.',
        'is_verified': True
    },
]

for data in review_data:
    try:
        doctor = Doctor.objects.get(id=data['doctor_id'])
        review = Review.objects.create(
            doctor=doctor,
            patient_name=data['patient_name'],
            patient_email=data['patient_email'],
            rating=data['rating'],
            comment=data['comment'],
            is_verified=data['is_verified']
        )
        print(f"Добавлен отзыв: {review.patient_name} для {doctor.first_name} {doctor.last_name}")
    except Doctor.DoesNotExist:
        print(f"Врач с id={data['doctor_id']} не найден")

print("Тестовые отзывы добавлены!")
