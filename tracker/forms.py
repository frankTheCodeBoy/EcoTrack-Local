from django import forms
from .models import EcoAction


class EcoActionForm(forms.ModelForm):
    class Meta:
        model = EcoAction
        fields = ['action_type', 'location']
        widgets = {
            'action_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter city with Country ('
                    'e.g., Nairobi, Kenya)'}),
        }
