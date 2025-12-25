from django import forms
from .models import Room, RoomCategory


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'number', 'category', 'capacity', 'has_child_bed',
            'status', 'description',
            'price_monday', 'price_tuesday', 'price_wednesday',
            'price_thursday', 'price_friday', 'price_saturday',
            'price_sunday', 'child_bed_price'
        ]
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
            'has_child_bed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_monday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_tuesday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_wednesday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_thursday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_friday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_saturday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_sunday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'child_bed_price': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = RoomCategory.objects.all()
        self.fields['child_bed_price'].help_text = "Максимум 1000 руб./сутки"


class RoomCategoryForm(forms.ModelForm):
    class Meta:
        model = RoomCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }