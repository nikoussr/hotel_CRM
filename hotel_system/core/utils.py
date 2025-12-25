from datetime import datetime, timedelta
from bookings.models import Booking


def get_week_dates(start_date=None):
    """Получить даты на неделю (пн-вс)"""
    if not start_date:
        start_date = datetime.now().date()

    # Находим понедельник этой недели
    start_of_week = start_date - timedelta(days=start_date.weekday())

    # Возвращаем список из 7 дней
    return [start_of_week + timedelta(days=i) for i in range(7)]


def get_room_occupancy(room, start_date, end_date):
    """Получить занятость номера на период"""
    bookings = Booking.objects.filter(
        room=room,
        check_in_date__lt=end_date,
        check_out_date__gt=start_date,
        status__in=['confirmed', 'pending_checkin', 'active']
    ).order_by('check_in_date')

    return bookings


def get_calendar_data(start_date=None):
    """Получить данные для календаря"""
    from rooms.models import Room

    week_dates = get_week_dates(start_date)
    rooms = Room.objects.all().order_by('number')

    calendar_data = []

    for room in rooms:
        room_info = {
            'id': room.id,
            'number': room.number,
            'category': room.category.name,
            'capacity': room.capacity,
            'status': room.status,
            'has_child_bed': room.has_child_bed,
            'days': []
        }

        # Получаем бронирования для этой комнаты на эту неделю
        bookings = get_room_occupancy(room, week_dates[0], week_dates[-1] + timedelta(days=1))

        # Для каждого дня недели определяем статус
        for date in week_dates:
            day_status = {
                'date': date,
                'status': 'available',
                'booking_id': None,
                'booking_type': None,
                'guest_name': '',
                'is_checkin': False,
                'is_checkout': False,
            }

            # Проверяем каждое бронирование
            for booking in bookings:
                if date >= booking.check_in_date and date < booking.check_out_date:
                    day_status['status'] = booking.get_booking_type()
                    day_status['booking_id'] = booking.id
                    day_status['guest_name'] = str(booking.guest)

                    # Проверяем, это день заезда или выезда?
                    if date == booking.check_in_date:
                        day_status['is_checkin'] = True
                    if date == booking.check_out_date - timedelta(days=1):
                        day_status['is_checkout'] = True
                    break

            room_info['days'].append(day_status)

        calendar_data.append(room_info)

    return {
        'week_dates': week_dates,
        'rooms': calendar_data,
        'start_date': week_dates[0],
        'end_date': week_dates[-1],
    }



def get_navigation_dates(start_date):
    """Получить даты для навигации по неделям"""
    prev_week = start_date - timedelta(days=7)
    next_week = start_date + timedelta(days=7)

    return {
        'prev_week': prev_week,
        'next_week': next_week,
        'current_week': start_date.replace(day=1),  # Примерно начало текущей недели
    }