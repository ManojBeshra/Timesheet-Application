# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from authentication.models import UserProfile  # adjust if needed

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # ✅ Do NOT set last_password_change
        UserProfile.objects.create(user=instance)
