from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from rooms.models import Room
from decimal import Decimal
from django.utils import timezone
from rooms.models import Room

class Guest(models.Model):
    """Гость/клиент"""
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    passport_data = models.CharField('Паспортные данные', max_length=200, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Гость'
        verbose_name_plural = 'Гости'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Booking(models.Model):
    """Бронирование номера"""

    class BookingStatus(models.TextChoices):
        CONFIRMED = 'confirmed', 'Подтверждено'
        PENDING_CHECKIN = 'pending_checkin', 'Ожидает заезда'
        ACTIVE = 'active', 'Активно (гость в номере)'
        COMPLETED = 'completed', 'Завершено'
        CANCELLED = 'cancelled', 'Отменено'

    # Основная информация
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name='Номер',
        related_name='bookings'
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.PROTECT,
        verbose_name='Гость',
        related_name='bookings'
    )

    # Даты
    check_in_date = models.DateField('Дата заезда')
    check_out_date = models.DateField('Дата выезда')
    actual_check_in = models.DateTimeField('Фактический заезд', null=True, blank=True)
    actual_check_out = models.DateTimeField('Фактический выезд', null=True, blank=True)

    # Гости
    adults = models.IntegerField(
        'Взрослых',
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    children = models.IntegerField('Детей', default=0)
    with_child_bed = models.BooleanField('Детская кровать', default=False)

    # Стоимость
    base_price = models.DecimalField(
        'Базовая стоимость',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    child_bed_price = models.DecimalField(
        'Стоимость детской кровати',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        'Сумма скидки',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        'Итоговая стоимость',
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Статус и информация
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED
    )
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f'Бронирование #{self.id} - {self.guest}'

    def calculate_total_price(self):
        """Рассчитать общую стоимость бронирования"""
        from datetime import timedelta

        # Рассчитываем количество ночей
        nights = (self.check_out_date - self.check_in_date).days

        # Расчет базовой стоимости по дням недели
        base_total = Decimal('0')
        current_date = self.check_in_date

        for _ in range(nights):
            day_of_week = current_date.weekday()  # 0=понедельник, 6=воскресенье
            daily_price = self.room.get_price_for_day(day_of_week)
            base_total += daily_price
            current_date += timedelta(days=1)

        self.base_price = base_total

        # Расчет стоимости детской кровати
        child_bed_total = Decimal('0')
        if self.with_child_bed:
            child_bed_total = self.room.child_bed_price * nights
            if child_bed_total > 1000 * nights:  # Ограничение 1000 руб/сутки
                child_bed_total = 1000 * nights

        self.child_bed_price = child_bed_total

        # Применение скидки за длительное проживание
        discount = Decimal('0')
        discount_rules = DiscountRule.objects.all().order_by('-min_nights')

        for rule in discount_rules:
            if nights >= rule.min_nights:
                discount = (base_total + child_bed_total) * (rule.percent / Decimal('100'))
                break

        self.discount_amount = discount

        # Итоговая стоимость
        self.total_price = base_total + child_bed_total - discount

        return self.total_price

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем стоимость при сохранении
        if not self.pk or 'force_recalculate' in kwargs:
            self.calculate_total_price()
        super().save(*args, **kwargs)

    def get_occupancy_status(self, date):
        """Получить статус занятости для конкретной даты"""
        if date < self.check_in_date:
            return None
        elif date >= self.check_out_date:
            return None
        else:
            return self.status

    def get_booking_type(self):
        """Получить тип бронирования для отображения в календаре"""
        if self.status == self.BookingStatus.CONFIRMED:
            return 'confirmed'
        elif self.status == self.BookingStatus.PENDING_CHECKIN:
            return 'pending'
        elif self.status == self.BookingStatus.ACTIVE:
            return 'active'
        elif self.status == self.BookingStatus.COMPLETED:
            return 'completed'
        elif self.status == self.BookingStatus.CANCELLED:
            return 'cancelled'
        return 'unknown'

    def check_in(self):
        """Зарегистрировать заезд"""
        from django.utils import timezone
        from rooms.models import Room

        # Проверяем текущий статус
        print(
            f"DEBUG check_in: current status = {self.status}, allowed = {[self.BookingStatus.CONFIRMED, self.BookingStatus.PENDING_CHECKIN]}")

        # Можно заселить из статусов "confirmed" или "pending_checkin"
        allowed_statuses = [self.BookingStatus.CONFIRMED, self.BookingStatus.PENDING_CHECKIN]

        if str(self.status) in allowed_statuses:
            self.status = self.BookingStatus.ACTIVE
            self.actual_check_in = timezone.now()

            # Обновляем статус номера
            self.room.status = Room.RoomStatus.OCCUPIED
            self.room.save()

            self.save(force_update=True)
            print(f"DEBUG check_in: success, new status = {self.status}")
            return True

        print(f"DEBUG check_in: failed")
        return False

    def check_out(self):
        """Зарегистрировать выезд"""
        if str(self.status) == self.BookingStatus.ACTIVE:
            self.status = self.BookingStatus.COMPLETED
            self.actual_check_out = timezone.now()

            # Обновляем статус номера
            self.room.status = Room.RoomStatus.MAINTENANCE
            self.room.save()

            self.save(force_update=True)
            print(f"DEBUG check_out: success, new status = {self.status}")
            return True

        print(f"DEBUG check_out: failed")
        return False

    def cancel_booking(self):
        """Отменить бронирование"""
        # Можно отменить из статусов "confirmed" или "pending_checkin"
        allowed_statuses = [self.BookingStatus.CONFIRMED, self.BookingStatus.PENDING_CHECKIN]

        if str(self.status) in allowed_statuses:
            self.status = self.BookingStatus.CANCELLED

            # Освобождаем номер
            self.room.status = Room.RoomStatus.AVAILABLE
            self.room.save()

            self.save(force_update=True)
            print(f"DEBUG cancel: success, new status = {self.status}")
            return True

        print(f"DEBUG cancel: failed")
        return False

    def get_nights_count(self):
        """Получить количество ночей"""
        return (self.check_out_date - self.check_in_date).days

    def get_daily_prices(self):
        """Получить детализацию по стоимости по дням"""
        from datetime import timedelta
        daily_prices = []
        current_date = self.check_in_date

        for i in range(self.get_nights_count()):
            day_of_week = current_date.weekday()
            daily_price = self.room.get_price_for_day(day_of_week)
            daily_prices.append({
                'date': current_date,
                'day_of_week': day_of_week,
                'price': daily_price
            })
            current_date += timedelta(days=1)

        return daily_prices


class DiscountRule(models.Model):
    """Правило скидки за длительное проживание"""
    name = models.CharField('Название', max_length=100)
    min_nights = models.IntegerField('Минимальное количество ночей')
    percent = models.DecimalField(
        'Процент скидки',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Правило скидки'
        verbose_name_plural = 'Правила скидок'
        ordering = ['min_nights']

    def __str__(self):
        return f'{self.name} ({self.min_nights}+ ночей: -{self.percent}%)'


