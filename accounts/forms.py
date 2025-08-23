from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class CombinedProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username
        self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data['username']
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save()
            profile.save()
        return profile


class CustomSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken. Try another.")
        return username
