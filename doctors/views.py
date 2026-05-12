import re

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from .models import Doctor, Review, DoctorBooking
from .forms import ReviewForm, DoctorBookingForm
from patients.models import Patient

def doctor_list(request):
    doctors = Doctor.objects.all()
    is_patient = request.user.is_authenticated and Patient.objects.filter(user=request.user).exists()
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors, 'is_patient': is_patient})


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    reviews = doctor.reviews.filter(is_verified=True)
    booking_form = DoctorBookingForm(doctor=doctor)
    review_form = ReviewForm()
    is_patient = request.user.is_authenticated and Patient.objects.filter(user=request.user).exists()
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'booking_form': booking_form,
        'review_form': review_form,
        'average_rating': doctor.get_average_rating(),
        'is_patient': is_patient,
    }
    return render(request, 'doctors/doctor_detail.html', context)


def add_review(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.save()
            return redirect('doctor_detail', pk=pk)
    else:
        form = ReviewForm()
    
    context = {'doctor': doctor, 'form': form}
    return render(request, 'doctors/add_review.html', context)


def get_available_slots(request, pk):
    """AJAX endpoint для получения свободных слотов"""
    doctor = get_object_or_404(Doctor, pk=pk)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Не позволяем записываться на прошедшие даты
    if date < datetime.now().date():
        return JsonResponse({'slots': []})
    
    slots = doctor.get_available_slots(date)
    
    return JsonResponse({
        'slots': [
            {
                'time': slot['time'].strftime('%H:%M'),
                'datetime': slot['datetime'].isoformat(),
            }
            for slot in slots
        ]
    })


@login_required(login_url='home')
def book_appointment(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorBookingForm(request.POST, doctor=doctor, patient=patient)
        
        if form.is_valid():
            # Получаем дату и время из очищенных данных
            date_value = form.cleaned_data.get('appointment_date_field')
            time_value = form.cleaned_data.get('appointment_time_field')
            
            if date_value and time_value:
                try:
                    # date_value это объект date, преобразуем в строку
                    date_str = date_value.strftime('%Y-%m-%d')
                    appointment_date = datetime.strptime(f"{date_str} {time_value}", '%Y-%m-%d %H:%M')
                    
                    booking = form.save(commit=False)
                    booking.doctor = doctor
                    booking.appointment_date = appointment_date
                    booking.patient_email = patient.email
                    booking.save()
                    return redirect('my_bookings')
                except (ValueError, AttributeError) as e:
                    form.add_error(None, f'Ошибка обработки даты/времени: {str(e)}')
        # Если форма не валидна или есть ошибка обработки даты, форма переотправляется с ошибками
    else:
        form = DoctorBookingForm(doctor=doctor, patient=patient)
    
    context = {'doctor': doctor, 'form': form}
    return render(request, 'doctors/book_appointment.html', context)


def my_bookings(request):
    phone = request.GET.get('phone', '')
    bookings = []
    
    if phone:
        cleaned_phone = re.sub(r'\D', '', phone)
        bookings = DoctorBooking.objects.filter(patient_phone=cleaned_phone)
    
    context = {
        'bookings': bookings,
        'phone': phone,
    }
    return render(request, 'doctors/my_bookings.html', context)


@login_required(login_url='doctor_login')
def doctor_dashboard(request):
    """Личный кабинет врача со списком записей"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_list')
    
    # Получение записей врача
    bookings = DoctorBooking.objects.filter(doctor=doctor).order_by('-appointment_date')
    
    # Список уникальных пациентов по контактным данным
    unique_patients = []
    seen = set()
    for booking in bookings:
        key = (booking.patient_name, booking.patient_phone)
        if key not in seen:
            seen.add(key)
            unique_patients.append({
                'name': booking.patient_name,
                'phone': booking.patient_phone,
                'last_visit': booking.appointment_date,
                'status': booking.get_status_display(),
            })
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'doctor': doctor,
        'bookings': bookings,
        'patients': unique_patients,
        'status_filter': status_filter,
        'status_choices': DoctorBooking.STATUS_CHOICES,
    }
    return render(request, 'doctors/doctor_dashboard.html', context)


@login_required(login_url='doctor_login')
def update_booking_status(request, pk):
    """Обновление статуса записи"""
    booking = get_object_or_404(DoctorBooking, pk=pk)
    
    # Проверка, что это врач этого пациента
    try:
        doctor = Doctor.objects.get(user=request.user)
        if booking.doctor != doctor:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(DoctorBooking.STATUS_CHOICES):
            booking.status = new_status
            if notes:
                booking.notes = notes
            booking.save()
            return JsonResponse({'success': True, 'message': 'Статус обновлён'})
        
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url='doctor_login')
def create_booking(request):
    """Врач сам создаёт запись пациента"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_list')
    
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        patient_phone = request.POST.get('patient_phone')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        # Создание datetime из даты и времени
        try:
            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            return render(request, 'doctors/create_booking.html', {
                'doctor': doctor,
                'error': 'Некорректная дата или время'
            })
        
        # Проверка, не занято ли время
        existing = DoctorBooking.objects.filter(
            doctor=doctor,
            appointment_date=appointment_datetime,
            status__in=['pending', 'confirmed']
        ).exists()
        
        if existing:
            return render(request, 'doctors/create_booking.html', {
                'doctor': doctor,
                'error': 'Это время уже занято'
            })
        
        booking = DoctorBooking.objects.create(
            doctor=doctor,
            patient_name=patient_name,
            patient_email='',  # Empty email, using phone for contact
            patient_phone=patient_phone,
            appointment_date=appointment_datetime,
            reason=reason,
            status='confirmed'  # Врач сам назначает, сразу confirmed
        )
        
        return redirect('doctor_dashboard')
    
    return render(request, 'doctors/create_booking.html', {'doctor': doctor})


def doctor_login(request):
    """Вход врача"""
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
            return redirect('doctor_dashboard')
        except Doctor.DoesNotExist:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Проверяем, что это врач
            try:
                doctor = Doctor.objects.get(user=user)
                login(request, user)
                return redirect('doctor_dashboard')
            except Doctor.DoesNotExist:
                return render(request, 'doctors/doctor_login.html', {
                    'error': 'Это не учётная запись врача'
                })
        else:
            return render(request, 'doctors/doctor_login.html', {
                'error': 'Неверное имя пользователя или пароль'
            })
    
    return render(request, 'doctors/doctor_login.html')


def doctor_logout(request):
    """Выход врача"""
    logout(request)
    return redirect('doctor_list')


def doctor_register(request):
    """Регистрация врача (только через админ-панель)"""
    return render(request, 'doctors/doctor_register.html', {
        'error': 'Регистрация врачей осуществляется через администратора клиники. Обратитесь в администрацию для получения учётных данных.'
    })


