from django.db import models
from django.core.validators import MinValueValidator
from bookings.models import Booking


class Payment(models.Model):
    """Платеж по бронированию"""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        CARD = 'card', 'Банковская карта'
        TRANSFER = 'transfer', 'Банковский перевод'
        ONLINE = 'online', 'Онлайн-оплата'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PARTIAL = 'partial', 'Частично оплачено'
        PAID = 'paid', 'Оплачено полностью'
        REFUNDED = 'refunded', 'Возвращено'
        CANCELLED = 'cancelled', 'Отменено'

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name='Бронирование',
        related_name='payments'
    )
    amount = models.DecimalField(
        'Сумма платежа',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateTimeField('Дата и время платежа', auto_now_add=True)
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    status = models.CharField(
        'Статус платежа',
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PAID
    )
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f'Платеж #{self.id} - {self.amount} руб.'