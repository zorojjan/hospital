import re

from django import forms
from .models import Review, DoctorBooking
from datetime import datetime, timedelta

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['patient_name', 'patient_email', 'rating', 'comment']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваш отзыв...'
            }),
        }


class DoctorBookingForm(forms.ModelForm):
    appointment_date_field = forms.DateField(
        label='Выберите дату приёма',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.now().strftime('%Y-%m-%d')
        })
    )
    
    appointment_time_field = forms.ChoiceField(
        label='Выберите время приёма',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )

    class Meta:
        model = DoctorBooking
        fields = ['patient_name', 'patient_phone', 'reason']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
                'required': True
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+996504232434',
                'inputmode': 'tel',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Причина визита...',
                'required': True
            }),
        }

    def __init__(self, *args, doctor=None, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor
        self.patient = patient
        # Устанавливаем минимальную дату на завтра
        min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.fields['appointment_date_field'].widget.attrs['min'] = min_date
        # Устанавливаем максимальную дату на 30 дней в будущем
        max_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.fields['appointment_date_field'].widget.attrs['max'] = max_date
        
        # Устанавливаем пустой вариант для выбора времени по умолчанию
        self.fields['appointment_time_field'].choices = [('', 'Выберите время...')]

        # Если форма привязана данными, подставляем доступные варианты времени
        if self.is_bound and self.doctor:
            date_str = self.data.get('appointment_date_field')
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    slots = self.doctor.get_available_slots(date)
                    if slots:
                        self.fields['appointment_time_field'].choices = [('', 'Выберите время...')] + [
                            (slot['time'].strftime('%H:%M'), slot['time'].strftime('%H:%M'))
                            for slot in slots
                        ]
                except ValueError:
                    pass
        
        # Автоматически заполняем данные пациента если он передан
        if patient:
            self.fields['patient_name'].initial = f"{patient.first_name} {patient.last_name}"
            self.fields['patient_phone'].initial = patient.phone

    def clean_patient_name(self):
        name = self.cleaned_data.get('patient_name', '').strip()
        if not name:
            raise forms.ValidationError('Введите ваше имя')
        if len(name) < 2:
            raise forms.ValidationError('Имя должно содержать минимум 2 символа')
        return name

    def clean_patient_phone(self):
        phone = self.cleaned_data.get('patient_phone', '')
        if not phone:
            raise forms.ValidationError('Введите номер телефона')
        normalized = re.sub(r'\D', '', phone)
        if len(normalized) < 9:
            raise forms.ValidationError('Телефон должен содержать минимум 9 цифр')
        return normalized

    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()
        if not reason:
            raise forms.ValidationError('Укажите причину визита')
        if len(reason) < 5:
            raise forms.ValidationError('Причина должна содержать минимум 5 символов')
        return reason

    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('appointment_date_field')
        time_value = cleaned_data.get('appointment_time_field')

        # Проверяем что оба поля заполнены
        if not date_value:
            raise forms.ValidationError('Выберите дату приёма')
        if not time_value:
            raise forms.ValidationError('Выберите время приёма')

        if date_value and time_value:
            try:
                # date_value уже объект date, преобразуем в строку
                date_str = date_value.strftime('%Y-%m-%d') if hasattr(date_value, 'strftime') else str(date_value)
                appointment_datetime = datetime.strptime(f"{date_str} {time_value}", '%Y-%m-%d %H:%M')
            except (ValueError, AttributeError) as e:
                raise forms.ValidationError(f'Неверный формат даты или времени записи: {str(e)}')

            if self.doctor:
                existing = DoctorBooking.objects.filter(
                    doctor=self.doctor,
                    appointment_date__date=appointment_datetime.date(),
                    appointment_date__hour=appointment_datetime.hour,
                    status__in=['pending', 'confirmed']
                ).exists()
                if existing:
                    raise forms.ValidationError('Врач уже занят в этот час. Выберите другой час.')

        return cleaned_data
