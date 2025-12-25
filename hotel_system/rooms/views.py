from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Room, RoomCategory
from .forms import RoomForm


@login_required
def room_list(request):
    """Список номеров"""
    rooms = Room.objects.all().order_by('number')

    # Фильтрация
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    capacity_filter = request.GET.get('capacity')

    if category_filter:
        rooms = rooms.filter(category_id=category_filter)
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if capacity_filter:
        rooms = rooms.filter(capacity=capacity_filter)

    categories = RoomCategory.objects.all()

    context = {
        'rooms': rooms,
        'categories': categories,
        'room_statuses': Room.RoomStatus.choices,
        'selected_category': category_filter,
        'selected_status': status_filter,
        'selected_capacity': capacity_filter,
    }

    return render(request, 'rooms/room_list.html', context)


@login_required
def room_detail(request, room_id):
    """Детальная информация о номере"""
    room = get_object_or_404(Room, id=room_id)

    # Активные бронирования для этого номера
    from bookings.models import Booking
    active_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'pending_checkin', 'active']
    ).order_by('check_in_date')

    # История бронирований
    booking_history = Booking.objects.filter(
        room=room
    ).exclude(status__in=['confirmed', 'pending_checkin', 'active']).order_by('-check_out_date')[:10]

    context = {
        'room': room,
        'active_bookings': active_bookings,
        'booking_history': booking_history,
    }

    return render(request, 'rooms/room_detail.html', context)


@login_required
def room_create(request):
    """Создание нового номера"""
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Номер {room.number} успешно создан')
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm()

    context = {
        'form': form,
        'title': 'Создание нового номера',
    }

    return render(request, 'rooms/room_form.html', context)


@login_required
def room_update(request, room_id):
    """Редактирование номера"""
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Номер {room.number} успешно обновлен')
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)

    context = {
        'form': form,
        'room': room,
        'title': f'Редактирование номера {room.number}',
    }

    return render(request, 'rooms/room_form.html.html', context)


@login_required
def room_delete(request, room_id):
    """Удаление номера"""
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        room_number = room.number
        room.delete()
        messages.success(request, f'Номер {room_number} успешно удален')
        return redirect('rooms:room_list')

    return render(request, 'rooms/room_confirm_delete.html', {'room': room})