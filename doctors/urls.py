from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('<int:pk>/book/', views.book_appointment, name='book_appointment'),
    path('<int:pk>/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('login/', views.doctor_login, name='doctor_login'),
    path('register/', views.doctor_register, name='doctor_register'),
    path('logout/', views.doctor_logout, name='doctor_logout'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('booking/<int:pk>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('create-booking/', views.create_booking, name='create_booking'),
]