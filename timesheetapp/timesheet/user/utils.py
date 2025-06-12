from django.contrib.auth.models import User
from .models import ManagerAssignment






def get_visible_users(user):
    if user.profile.role == 'admin':
        return User.objects.all()
    elif user.profile.role == 'manager':
        assigned_ids = ManagerAssignment.objects.filter(manager=user).values_list('user_id', flat=True)
        return User.objects.filter(id__in=assigned_ids) | User.objects.filter(id=user.id)
    else:
        return User.objects.filter(id=user.id)
