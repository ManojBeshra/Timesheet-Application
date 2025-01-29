from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class priority_type(models.Model):
   priority_name = models.CharField(max_length=100)
   def __str__(self):
        return f"{self.priority_name}"


class task_type(models.Model):
  tasktype_id = models.IntegerField(primary_key= True)
  name = models.CharField(max_length=100, null = True)

  def __str__(self):
    return f"{self.name}"

class state(models.Model):
   state_name = models.CharField(max_length=100, null = True)
   
   def __str__(self):
    return f"{self.state_name}"

class ticket(models.Model):
    ticket_name = models.CharField(max_length=200, null=False)
    customer = models.ForeignKey('customer.customer_contact', on_delete=models.CASCADE, null=True)
    ticket_type = models.ForeignKey(task_type, on_delete=models.CASCADE, null=True )
    date_opened = models.DateField(null=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null = True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    last_updated = models.DateField(null=True)
    state = models.ForeignKey(state, on_delete=models.CASCADE, null=True)
    short_description = models.CharField(max_length=200, null=True)
    comments = models.CharField(max_length=200, null=True)
    user_comments = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.ticket_name}"

class ticket_detail(models.Model):
    ticket = models.ForeignKey(ticket, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    detail = models.CharField(max_length=300, null=True)

    def __str__(self):
        return f"{self.ticket.ticket_name}"
