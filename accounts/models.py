from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(
        blank=True, null=True, max_length=500)  # 🆕 Optional user bio/status
    total_actions = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)  # 🆕 Weighted score tracker
    badge_level = models.CharField(max_length=50, default="🌱 Newcomer")

    def __str__(self):
        return f"{self.user.username}'s Profile"
