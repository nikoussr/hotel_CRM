from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RoomCategory(models.Model):
    """Категория номера"""
    name = models.CharField('Название', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    """Номер гостиницы"""

    class RoomStatus(models.TextChoices):
        AVAILABLE = 'available', 'Доступен'
        BOOKED = 'booked', 'Забронирован'
        OCCUPIED = 'occupied', 'Занят'
        MAINTENANCE = 'maintenance', 'На обслуживании'

    # Основная информация
    number = models.CharField('Номер комнаты', max_length=10, unique=True)
    category = models.ForeignKey(
        RoomCategory,
        on_delete=models.PROTECT,
        verbose_name='Категория'
    )
    capacity = models.IntegerField(
        'Вместимость (человек)',
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    has_child_bed = models.BooleanField('Возможность детской кровати', default=False)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE
    )
    description = models.TextField('Описание номера', blank=True)

    # Цены по дням недели (в рублях)
    price_monday = models.DecimalField(
        'Цена за понедельник',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_tuesday = models.DecimalField(
        'Цена за вторник',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_wednesday = models.DecimalField(
        'Цена за среду',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_thursday = models.DecimalField(
        'Цена за четверг',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_friday = models.DecimalField(
        'Цена за пятницу',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_saturday = models.DecimalField(
        'Цена за субботу',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    price_sunday = models.DecimalField(
        'Цена за воскресенье',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Дополнительные услуги
    child_bed_price = models.DecimalField(
        'Цена детской кровати (за сутки)',
        max_digits=10,
        decimal_places=2,
        default=500
    )

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['number']

    def __str__(self):
        return f'Номер {self.number} ({self.category})'

    def get_price_for_day(self, day_of_week):
        """Получить цену для конкретного дня недели (0=понедельник, 6=воскресенье)"""
        price_map = {
            0: self.price_monday,
            1: self.price_tuesday,
            2: self.price_wednesday,
            3: self.price_thursday,
            4: self.price_friday,
            5: self.price_saturday,
            6: self.price_sunday,
        }
        return price_map.get(day_of_week, 0)