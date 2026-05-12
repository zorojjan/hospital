import re

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from .models import Patient
from doctors.models import DoctorBooking

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})


def patient_login(request):
    """Вход пациента"""
    if request.user.is_authenticated:
        try:
            patient = Patient.objects.get(user=request.user)
            return redirect('patient_dashboard')
        except Patient.DoesNotExist:
            pass
    
    if request.method == 'POST':
        login_value = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=login_value, password=password)
        if user is None:
            normalized_login = re.sub(r'\D', '', login_value or '')
            if normalized_login and normalized_login != login_value:
                user = authenticate(request, username=normalized_login, password=password)
        
        if user is not None:
            # Проверяем, что это пациент
            try:
                patient = Patient.objects.get(user=user)
                login(request, user)
                return redirect('patient_dashboard')
            except Patient.DoesNotExist:
                return render(request, 'patients/patient_login.html', {
                    'error': 'Это не учётная запись пациента'
                })
        else:
            return render(request, 'patients/patient_login.html', {
                'error': 'Неверное имя пользователя или пароль'
            })
    
    return render(request, 'patients/patient_login.html')


def patient_logout(request):
    """Выход пациента"""
    logout(request)
    return redirect('home')


def patient_register(request):
    """Регистрация пациента"""
    if request.user.is_authenticated:
        try:
            patient = Patient.objects.get(user=request.user)
            return redirect('patient_dashboard')
        except Patient.DoesNotExist:
            pass

    from hospital.forms import UnifiedRegisterForm

    form = UnifiedRegisterForm()
    if request.method == 'POST':
        form = UnifiedRegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = re.sub(r'\D', '', phone or '')
            
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                Patient.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    phone=username
                )
                login(request, user)
                return redirect('patient_dashboard')
            except Exception as e:
                form.add_error(None, f'Ошибка регистрации: {str(e)}')

    return render(request, 'patients/patient_register.html', {'form': form})


@login_required(login_url='patient_login')
def patient_dashboard(request):
    """Личный кабинет пациента"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_list')
    
    # Получение записей пациента
    bookings_filter = Q(patient_phone=patient.phone)
    if patient.email:
        bookings_filter |= Q(patient_email=patient.email)
    bookings = DoctorBooking.objects.filter(bookings_filter).order_by('-appointment_date')
    
    # Добавляем информацию о возможности оценки для каждой записи
    for booking in bookings:
        if booking.status == 'completed':
            # Проверяем, есть ли уже оценка от этого пациента
            has_review = booking.doctor.reviews.filter(patient_email=patient.email, is_verified=True).exists()
            booking.can_review = not has_review
            booking.has_review = has_review
        else:
            booking.can_review = False
            booking.has_review = False
    
    # Статистика
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status='completed').count()
    upcoming_bookings = bookings.filter(status__in=['pending', 'confirmed']).count()
    
    context = {
        'patient': patient,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'upcoming_bookings': upcoming_bookings,
    }
    return render(request, 'patients/patient_dashboard.html', context)


@login_required(login_url='patient_login')
def patient_my_bookings(request):
    """История записей пациента"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_list')
    
    bookings_filter = Q(patient_phone=patient.phone)
    if patient.email:
        bookings_filter |= Q(patient_email=patient.email)
    bookings = DoctorBooking.objects.filter(bookings_filter).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'bookings': bookings,
    }
    return render(request, 'patients/patient_bookings.html', context)
