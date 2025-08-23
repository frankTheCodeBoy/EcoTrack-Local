from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.log_action,
        name='log_action'),
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'),
    path(
        'profile/',
        views.profile_view,
        name='profile'),  # 👤 New profile route
    path(
        'leaderboard/',
        views.leaderboard,
        name='leaderboard'),
    path(
        'certificate/',
        views.download_certificate,
        name='download_certificate'),
    path('region-summary/',
         views.region_summary,
         name='region_summary'),
    path(
        'trigger-error/',
        views.trigger_error),
]
