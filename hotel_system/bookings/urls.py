from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('quick-booking/', views.quick_booking, name='quick_booking'),
    path('check-availability/', views.check_room_availability, name='check_availability'),

    # Гости
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/create/', views.guest_create, name='guest_create'),
    path('guests/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('guests/<int:guest_id>/update/', views.guest_update, name='guest_update'),

    # Бронирования
    path('', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/manage/', views.booking_manage, name='booking_manage'),
    path('<int:booking_id>/update-dates/', views.booking_update_dates, name='booking_update_dates'),
]