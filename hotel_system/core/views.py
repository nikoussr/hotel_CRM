from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from django.views.decorators.http import require_POST

from .utils import get_calendar_data, get_week_dates, get_navigation_dates
from bookings.models import Booking, Guest
from rooms.models import Room
import json


@login_required
def dashboard(request):
    """Главная страница с календарем"""
    # Получаем параметры даты из GET-запроса
    start_date_str = request.GET.get('start_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            start_date = None
    else:
        start_date = None

    # Получаем данные для календаря
    calendar_data = get_calendar_data(start_date)
    nav_dates = get_navigation_dates(calendar_data['start_date'])

    # Статистика для дашборда
    today = timezone.now().date()

    # Заезды сегодня
    checkins_today = Booking.objects.filter(
        check_in_date=today,
        status__in=['confirmed', 'pending_checkin']
    ).count()

    # Выселения сегодня
    checkouts_today = Booking.objects.filter(
        check_out_date=today,
        status__in=['confirmed', 'pending_checkin', 'active']
    ).count()

    # Занято номеров
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    booked_rooms = Room.objects.filter(status='booked').count()

    # Ближайшие бронирования
    upcoming_bookings = Booking.objects.filter(
        check_in_date__gte=today,
        status='confirmed'
    ).order_by('check_in_date')[:5]

    # Текущие гости
    current_guests = Booking.objects.filter(
        status='active'
    ).select_related('guest', 'room')

    context = {
        'today': today,
        'checkins_today': checkins_today,
        'checkouts_today': checkouts_today,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'booked_rooms': booked_rooms,
        'upcoming_bookings': upcoming_bookings,
        'current_guests': current_guests,
        'prev_week': nav_dates['prev_week'],
        'next_week': nav_dates['next_week'],
        **calendar_data,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
@require_POST
def quick_checkin(request, booking_id):
    """Быстрая регистрация заезда"""
    try:
        booking = Booking.objects.get(id=booking_id)
        if booking.check_in():
            messages.success(request, f'Гость {booking.guest} успешно зарегистрирован в номере {booking.room.number}')
        else:
            messages.error(request,
                           f'Невозможно зарегистрировать заезд. Текущий статус: {booking.get_status_display()}')
    except Booking.DoesNotExist:
        messages.error(request, 'Бронирование не найдено')

    return redirect('core:dashboard')


@login_required
@require_POST
def quick_checkout(request, booking_id):
    """Быстрая регистрация выезда"""
    try:
        booking = Booking.objects.get(id=booking_id)
        if booking.check_out():
            messages.success(request, f'Гость {booking.guest} успешно выселен из номера {booking.room.number}')
        else:
            messages.error(request,
                           f'Невозможно зарегистрировать выезд. Текущий статус: {booking.get_status_display()}')
    except Booking.DoesNotExist:
        messages.error(request, 'Бронирование не найдено')

    return redirect('core:dashboard')


@login_required
def quick_cancel(request, booking_id):
    """Быстрая отмена бронирования"""
    try:
        booking = Booking.objects.get(id=booking_id)
        if booking.cancel_booking():
            messages.success(request, f'Бронирование #{booking.id} успешно отменено')
        else:
            messages.error(request, 'Невозможно отменить это бронирование')
    except Booking.DoesNotExist:
        messages.error(request, 'Бронирование не найдено')

    return redirect('core:dashboard')