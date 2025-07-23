from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('User', 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    salaried = models.BooleanField()
    wages = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
   
class ManagerAssignment(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_manager')

    def __str__(self):
        return f"{self.manager.username} → {self.user.username}"

class Teams(models.Model):
    teamname = models.TextField()
    assigned_users = models.ManyToManyField(User)  # Allow multiple users

    def __str__(self):
            return f"{self.teamname}"