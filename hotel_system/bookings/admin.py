from django.contrib import admin
from .models import Guest, Booking, DiscountRule

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'email')
    search_fields = ('last_name', 'first_name', 'phone', 'email')
    list_filter = ('created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'guest', 'room', 'check_in_date',
        'check_out_date', 'status', 'total_price'
    )
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('guest__last_name', 'guest__first_name', 'room__number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('room', 'guest', 'status')
        }),
        ('Даты', {
            'fields': (
                'check_in_date', 'check_out_date',
                'actual_check_in', 'actual_check_out'
            )
        }),
        ('Гости', {
            'fields': ('adults', 'children', 'with_child_bed')
        }),
        ('Стоимость', {
            'fields': ('base_price', 'child_bed_price', 'discount_amount', 'total_price')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(DiscountRule)
class DiscountRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_nights', 'percent', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)