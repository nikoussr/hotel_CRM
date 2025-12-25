from django.contrib import admin
from .models import RoomCategory, Room

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'capacity', 'status', 'price_monday')
    list_filter = ('category', 'status', 'has_child_bed')
    search_fields = ('number', 'description')
    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'category', 'capacity', 'has_child_bed', 'status', 'description')
        }),
        ('Цены по дням недели', {
            'fields': (
                'price_monday', 'price_tuesday', 'price_wednesday',
                'price_thursday', 'price_friday', 'price_saturday',
                'price_sunday'
            )
        }),
        ('Дополнительные услуги', {
            'fields': ('child_bed_price',)
        }),
    )