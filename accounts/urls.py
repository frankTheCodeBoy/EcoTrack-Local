from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path(
        'login/',
        views.login_view,
        name='login'),
    path(
        'signup/',
        views.signup,
        name='signup'),
    path(
        'check-username/',
        views.check_username,
        name='check_username'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'),  # 👈 Redirect after logout
    path(
        'edit/',
        views.edit_profile,
        name='edit_profile'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html'),
        name='password_reset'),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
]
