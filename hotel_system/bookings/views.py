from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from .forms import QuickBookingForm
from .models import Booking, Guest, DiscountRule
from django.db.models import Q, Sum
from rooms.models import Room
from .forms import GuestForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def quick_booking(request):
    """Быстрое бронирование из календаря"""
    if request.method == 'POST':
        form = QuickBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(
                request,
                f'Бронирование создано! Номер: {booking.room.number}, '
                f'Гость: {booking.guest}, Стоимость: {booking.total_price} руб.'
            )
            return redirect('core:dashboard')
    else:
        # Устанавливаем начальные значения из GET-параметров
        initial_data = {}

        room_id = request.GET.get('room_id')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')

        if room_id:
            try:
                room = Room.objects.get(id=room_id)
                initial_data['room'] = room
            except Room.DoesNotExist:
                pass

        if check_in:
            try:
                initial_data['check_in_date'] = datetime.strptime(check_in, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        if check_out:
            try:
                initial_data['check_out_date'] = datetime.strptime(check_out, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        form = QuickBookingForm(initial=initial_data)

    return render(request, 'bookings/quick_booking.html', {'form': form})


@login_required
@require_POST
def check_room_availability(request):
    """Проверить доступность номера на даты (AJAX)"""
    room_id = request.POST.get('room_id')
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')

    try:
        room = Room.objects.get(id=room_id)
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

        # Проверяем доступность
        overlapping = Booking.objects.filter(
            room=room,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            status__in=['confirmed', 'pending_checkin', 'active']
        ).exists()

        available = not overlapping

        # Рассчитываем стоимость
        nights = (check_out - check_in).days
        total_price = 0

        if available and nights > 0:
            current_date = check_in
            for _ in range(nights):
                day_of_week = current_date.weekday()
                total_price += float(room.get_price_for_day(day_of_week))
                current_date += timedelta(days=1)

        return JsonResponse({
            'available': available,
            'nights': nights,
            'estimated_price': total_price,
            'room_number': room.number,
            'room_capacity': room.capacity,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def guest_list(request):
    """Список гостей"""
    guests = Guest.objects.all().order_by('last_name', 'first_name')

    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        guests = guests.filter(
            Q(last_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        'guests': guests,
        'search_query': search_query or '',
    }

    return render(request, 'bookings/guest_list.html', context)


@login_required
def guest_detail(request, guest_id):
    """Детальная информация о госте"""
    guest = get_object_or_404(Guest, id=guest_id)

    # Активные бронирования гостя
    active_bookings = Booking.objects.filter(
        guest=guest,
        status__in=['confirmed', 'pending_checkin', 'active']
    ).order_by('check_in_date')

    # История бронирований
    booking_history = Booking.objects.filter(
        guest=guest
    ).exclude(status__in=['confirmed', 'pending_checkin', 'active']).order_by('-check_out_date')

    # Статистика
    total_bookings = Booking.objects.filter(guest=guest).count()
    total_spent = Booking.objects.filter(
        guest=guest,
        status__in=['completed', 'active']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'guest': guest,
        'active_bookings': active_bookings,
        'booking_history': booking_history,
        'total_bookings': total_bookings,
        'total_spent': total_spent,
    }

    return render(request, 'bookings/guest_detail.html', context)

@login_required
def guest_create(request):
    """Создание нового гостя"""
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Гость {guest} успешно создан')
            return redirect('bookings:guest_detail', guest_id=guest.id)
    else:
        form = GuestForm()

    context = {
        'form': form,
        'title': 'Добавление нового гостя',
    }

    return render(request, 'bookings/guest_form.html', context)


@login_required
def guest_update(request, guest_id):
    """Редактирование гостя"""
    guest = get_object_or_404(Guest, id=guest_id)

    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Данные гостя {guest} обновлены')
            return redirect('bookings:guest_detail', guest_id=guest.id)
    else:
        form = GuestForm(instance=guest)

    context = {
        'form': form,
        'guest': guest,
        'title': f'Редактирование гостя {guest}',
    }

    return render(request, 'bookings/guest_form.html', context)


@login_required
def booking_list(request):
    """Список бронирований"""
    bookings = Booking.objects.all().select_related('guest', 'room').order_by('-created_at')

    # Фильтрация
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_from:
        bookings = bookings.filter(check_in_date__gte=date_from)
    if date_to:
        bookings = bookings.filter(check_out_date__lte=date_to)

    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(bookings, 20)  # 20 на странице

    try:
        bookings_page = paginator.page(page)
    except PageNotAnInteger:
        bookings_page = paginator.page(1)
    except EmptyPage:
        bookings_page = paginator.page(paginator.num_pages)

    context = {
        'bookings': bookings_page,
        'status_choices': Booking.BookingStatus.choices,
        'selected_status': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'bookings/booking_list.html', context)


@login_required
def booking_detail(request, booking_id):
    """Детальная информация о бронировании"""
    booking = get_object_or_404(Booking.objects.select_related('guest', 'room'), id=booking_id)

    # Платежи по этому бронированию
    try:
        from payments.models import Payment
        payments = Payment.objects.filter(booking=booking).order_by('-payment_date')

        # Сумма оплаченного
        total_paid = payments.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        balance = booking.total_price - total_paid
    except ImportError:
        payments = []
        total_paid = 0
        balance = booking.total_price

    context = {
        'booking': booking,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
        'daily_prices': booking.get_daily_prices(),
    }

    return render(request, 'bookings/booking_detail.html', context)


@login_required
def booking_manage(request, booking_id):
    """Управление бронированием: заселение, выселение, отмена"""
    booking = get_object_or_404(Booking.objects.select_related('guest', 'room'), id=booking_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'check_in':
            if booking.check_in():
                messages.success(request, f'Гость {booking.guest} успешно заселен в номер {booking.room.number}')
            else:
                messages.error(request, f'Невозможно заселить. Текущий статус: {booking.get_status_display()}')

        elif action == 'check_out':
            if booking.check_out():
                messages.success(request, f'Гость {booking.guest} успешно выселен из номера {booking.room.number}')
            else:
                messages.error(request, f'Невозможно выселить. Текущий статус: {booking.get_status_display()}')

        elif action == 'cancel':
            if booking.cancel_booking():
                messages.success(request, f'Бронирование #{booking.id} успешно отменено')
            else:
                messages.error(request, f'Невозможно отменить. Текущий статус: {booking.get_status_display()}')

        return redirect('bookings:booking_manage', booking_id=booking.id)

    context = {
        'booking': booking,
    }

    return render(request, 'bookings/booking_manage.html', context)


@login_required
def booking_update_dates(request, booking_id):
    """Обновление фактических дат заезда/выезда"""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        actual_check_in = request.POST.get('actual_check_in')
        actual_check_out = request.POST.get('actual_check_out')

        try:
            if actual_check_in:
                from django.utils.dateparse import parse_datetime
                check_in_dt = parse_datetime(actual_check_in)
                if check_in_dt:
                    booking.actual_check_in = check_in_dt

            if actual_check_out:
                from django.utils.dateparse import parse_datetime
                check_out_dt = parse_datetime(actual_check_out)
                if check_out_dt:
                    booking.actual_check_out = check_out_dt

            booking.save()
            messages.success(request, 'Фактические даты успешно обновлены')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении дат: {str(e)}')

        return redirect('bookings:booking_manage', booking_id=booking.id)

    return redirect('bookings:booking_detail', booking_id=booking_id)