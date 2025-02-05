from django.db import models
from django.contrib.auth.models import User
from customer.models import customer

# Create your models here.

class priority_type(models.Model):
   priority_name = models.CharField(max_length=100)
   def __str__(self):
        return f"{self.priority_name}"


class ticket_type(models.Model):
  name = models.CharField(max_length=100, null = True)

  def __str__(self):
    return f"{self.name}"

class state(models.Model):
   state_name = models.CharField(max_length=100, null = True)
   
   def __str__(self):
    return f"{self.state_name}"


class ticket(models.Model):
    ticket_id = models.CharField(max_length = 200, null = False)
    ticket_title = models.CharField(max_length=200, null=False)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE, null=True)
    ticket_type = models.ForeignKey(ticket_type, on_delete=models.CASCADE, null=True)
    date_opened = models.DateField(null=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null = True)
    # assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="assigned_to")
    assigned_to = models.ManyToManyField(User, related_name="assigned_tickets")  # Allow multiple users
    last_updated = models.DateTimeField(null=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name="last_updated_by")
    state = models.ForeignKey(state, on_delete=models.CASCADE, null=True)
    short_description = models.CharField(max_length=200, null=True)
    closed_date = models.DateField(null=True)
    solution = models.TextField(max_length=500, default="")


    def __str__(self):
        return f"{self.ticket_title}"
    
class ticket_update_history(models.Model):
    updated_on = models.DateTimeField(null = True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    changes = models.CharField(max_length=500, null = True)

    def __str__(self):
        return f"{self.changes}"