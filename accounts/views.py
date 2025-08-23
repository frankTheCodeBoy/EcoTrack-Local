from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import CombinedProfileForm, CustomSignUpForm
from django.contrib.auth.decorators import login_required


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def signup(request):
    form = CustomSignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'accounts/signup.html', {'form': form})


def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = CombinedProfileForm(
            request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CombinedProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
