from django import template

register = template.Library()

@register.filter
def get_status_class(status):
    """Получить CSS класс для статуса"""
    status_classes = {
        'available': 'status-available',
        'booked': 'bg-info text-white',
        'occupied': 'bg-success text-white',
        'maintenance': 'bg-secondary text-white',
        'confirmed': 'bg-info text-white',
        'pending_checkin': 'bg-warning text-white',
        'active': 'bg-success text-white',
        'completed': 'bg-light text-dark',
        'cancelled': 'bg-danger text-white',
    }
    return status_classes.get(status, 'bg-light text-dark')