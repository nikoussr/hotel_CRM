from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quick-checkin/<int:booking_id>/', views.quick_checkin, name='quick_checkin'),
    path('quick-checkout/<int:booking_id>/', views.quick_checkout, name='quick_checkout'),
    path('quick-cancel/<int:booking_id>/', views.quick_cancel, name='quick_cancel'),
]