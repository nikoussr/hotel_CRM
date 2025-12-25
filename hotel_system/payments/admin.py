from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_date', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('booking__guest__last_name', 'booking__guest__first_name', 'notes')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('booking', 'amount', 'status')
        }),
        ('Детали оплаты', {
            'fields': ('payment_method', 'payment_date')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at')
        }),
    )