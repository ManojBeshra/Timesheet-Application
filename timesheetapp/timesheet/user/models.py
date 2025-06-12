from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')


    def __str__(self):
        return f"{self.user.username} - {self.role}"
   




class ManagerAssignment(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_manager')


    def __str__(self):
        return f"{self.manager.username} → {self.user.username}"
