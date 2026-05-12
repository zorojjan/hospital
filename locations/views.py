from django.shortcuts import render
from .models import Clinic
from doctors.models import Doctor

def map_view(request):
    clinic = Clinic.objects.first()
    doctors = Doctor.objects.filter(latitude__isnull=False, longitude__isnull=False)
    context = {
        'clinic': clinic,
        'doctors': doctors
    }
    return render(request, 'locations/map.html', context)
