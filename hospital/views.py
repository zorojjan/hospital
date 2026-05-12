import re

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor
from patients.models import Patient
from .forms import UnifiedLoginForm
from .models import News


def normalize_phone_value(value):
    if not value:
        return value
    return re.sub(r'\D', '', value)


def home(request):
    """Главная страница"""
    featured_doctors = Doctor.objects.filter(is_featured=True)[:2]
    
    # Если пользователь уже входел, перенаправляем на его кабинет
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
            return redirect('doctor_dashboard')
        except Doctor.DoesNotExist:
            pass
        
        try:
            patient = Patient.objects.get(user=request.user)
            return redirect('patient_dashboard')
        except Patient.DoesNotExist:
            pass
    
    facts = [
        'Регулярная физическая активность улучшает работу сердца и мозга.',
        'Сон менее 7 часов увеличивает риск хронических заболеваний.',
        'Питание на 80% влияет на общее состояние здоровья.',
    ]

    news_list = News.objects.filter(is_published=True)[:3]

    context = {
        'featured_doctors': featured_doctors,
        'facts': facts,
        'news_list': news_list,
    }
    return render(request, 'home.html', context)


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    return redirect('home')