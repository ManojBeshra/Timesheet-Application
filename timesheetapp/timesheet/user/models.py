from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('User', 'User'),
    ]
    DESIGNATION_CHOICES = [
        ('Developer', 'Developer'),
        ('Assistant Developer', 'Assistant Developer'),
        ('Senior Developer', 'Senior Developer'),
        ('Operational Manager', 'Operational Manager'),
        ('CEO', 'CEO'),
        ('CFO', 'CFO'),
        ('CTO', 'CTO'),
        ('HR Manager', 'HR Manager'),
        ('Team Lead', 'Team Lead'),
        ('Intern', 'Intern'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    designation = models.CharField(max_length=30, choices=DESIGNATION_CHOICES, default='Developer')
    salaried = models.BooleanField()
    wages = models.DecimalField(max_digits=7, decimal_places=2)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=30, blank=True, null=True)

class ManagerAssignment(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_manager')

    def __str__(self):
        return f"{self.manager.username} → {self.user.username}"

class Teams(models.Model):
    teamname = models.TextField()
    assigned_users = models.ManyToManyField(User) 

    def __str__(self):
            return f"{self.teamname}"
    
