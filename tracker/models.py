from django.db import models
from django.contrib.auth.models import User  # Add this


class EcoAction(models.Model):
    ACTION_CHOICES = [
        ('walk', '🚶 Walked instead of driving'),
        ('solar', '☀️ Used solar power'),
        ('recycle', '♻️ Recycled waste'),
        ('plant', '🌳 Planted a tree'),
        ('refill', '🧴 Used refillable container'),
        ('bike', '🚴 Rode a bicycle'),
        ('compost', '🍂 Composted organic waste'),
        ('share', '📤 Shared eco tips online'),
        ('repair', '🔧 Repaired instead of replacing'),
        ('save_water', '💧 Conserved water'),]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True)  # ✅ Add this line
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(
        max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return (
            f"{self.get_action_type_display()}"
            f" at {self.timestamp.strftime('%Y-%m-%d')}")


class RegionInfo(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    emoji = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.emoji or '🌍'} {self.name}"
