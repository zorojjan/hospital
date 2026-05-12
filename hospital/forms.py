import re

from django import forms
from django.contrib.auth.models import User
from doctors.models import Doctor
from patients.models import Patient

class UnifiedLoginForm(forms.Form):
    """Форма для единого входа"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class UnifiedRegisterForm(forms.Form):
    """Форма для регистрации пациентов"""
    
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+996504232434',
            'inputmode': 'tel'
        })
    )
    
    password = forms.CharField(
        min_length=8,
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Минимум 8 символов'
        })
    )
    
    password_confirm = forms.CharField(
        min_length=8,
        label='Подтвердите пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        normalized = re.sub(r'\D', '', phone)
        if not normalized:
            raise forms.ValidationError('Введите корректный номер телефона')
        if not normalized.startswith('996') or len(normalized) != 12:
            raise forms.ValidationError('Номер должен быть в формате +996-XXX-XX-XX-XX')
        if User.objects.filter(username=normalized).exists():
            raise forms.ValidationError('Пользователь с таким номером телефона уже зарегистрирован')
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')

        return cleaned_data
