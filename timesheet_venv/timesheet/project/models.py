from django.db import models
from customer.models import customer
from django.contrib.auth.models import User

# Create your models here.

class project(models.Model):
    project_id = models.CharField(max_length = 200, null = False)
    name = models.CharField(max_length=200, null=False)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE, null=True)
    estimated_hr = models.IntegerField(null=True)
    completed_hr = models.IntegerField(null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects")  # Allow multiple users
    date = models.DateTimeField(null=True)
    estimated_complete_date = models.DateField(null=True)
    actual_complete_date = models.DateField(null=True)


    def __str__(self):
        return f"{self.name}"
