from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Guest
from rooms.models import Room


class QuickBookingForm(forms.ModelForm):
    """Форма для быстрого бронирования"""
    guest_first_name = forms.CharField(label='Имя', max_length=100)
    guest_last_name = forms.CharField(label='Фамилия', max_length=100)
    guest_phone = forms.CharField(label='Телефон', max_length=20)

    class Meta:
        model = Booking
        fields = ['room', 'check_in_date', 'check_out_date', 'adults', 'children', 'with_child_bed']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Фильтруем доступные номера
        available_rooms = Room.objects.filter(status='available')
        self.fields['room'].queryset = available_rooms
        self.fields['room'].empty_label = "Выберите номер"

        # Устанавливаем минимальные даты
        today = timezone.now().date()
        self.fields['check_in_date'].widget.attrs['min'] = today
        self.fields['check_out_date'].widget.attrs['min'] = today + timedelta(days=1)

    def clean(self):
        cleaned_data = super().clean()

        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')
        adults = cleaned_data.get('adults')

        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError('Дата выезда должна быть позже даты заезда')

            # Проверяем доступность номера
            if room:
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in,
                    status__in=['confirmed', 'pending_checkin', 'active']
                )

                if self.instance:
                    overlapping_bookings = overlapping_bookings.exclude(id=self.instance.id)

                if overlapping_bookings.exists():
                    raise ValidationError('Номер уже забронирован на выбранные даты')

        if adults and room:
            if adults > room.capacity:
                raise ValidationError(f'В номере максимальная вместимость: {room.capacity} взрослых')

        return cleaned_data

    def save(self, commit=True):
        # Создаем или находим гостя
        guest, created = Guest.objects.get_or_create(
            phone=self.cleaned_data['guest_phone'],
            defaults={
                'first_name': self.cleaned_data['guest_first_name'],
                'last_name': self.cleaned_data['guest_last_name'],
            }
        )

        # Если гость уже существует, обновляем имя если оно изменилось
        if not created:
            if (guest.first_name != self.cleaned_data['guest_first_name'] or
                    guest.last_name != self.cleaned_data['guest_last_name']):
                guest.first_name = self.cleaned_data['guest_first_name']
                guest.last_name = self.cleaned_data['guest_last_name']
                guest.save()

        # Создаем бронирование
        booking = super().save(commit=False)
        booking.guest = guest

        if commit:
            booking.save()
            # Обновляем статус номера
            room = booking.room
            room.status = 'booked'
            room.save()

        return booking


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['last_name', 'first_name', 'middle_name', 'phone', 'email', 'passport_data']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'passport_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Простая проверка на минимальную длину
        if len(phone) < 5:
            raise forms.ValidationError("Номер телефона слишком короткий")
        return phone