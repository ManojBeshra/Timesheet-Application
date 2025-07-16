from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from .models import EarnedLeaveDay
from django.contrib.auth.signals import user_logged_in


@receiver(post_save, sender=User)
def create_earned_leave_for_new_user(sender, instance, created, **kwargs):
    if created:
        joined_date = instance.date_joined.date()
        leave_days = EarnedLeaveDay(user=instance).calculate_earned_leave()

        EarnedLeaveDay.objects.create(
            user=instance,
            joined_date=joined_date,
            earned_leave_days=leave_days
        )


@receiver(user_logged_in)
def update_earned_leave_on_login(sender, user, request, **kwargs):
    try:
        leave_record, _ = EarnedLeaveDay.objects.get_or_create(user=user)
        new_earned_leave = leave_record.calculate_earned_leave()

        if leave_record.earned_leave_days != new_earned_leave:
            leave_record.earned_leave_days = new_earned_leave
            leave_record.save()

    except Exception as e:
        print(f"[EarnedLeave Update Error]: {e}")
