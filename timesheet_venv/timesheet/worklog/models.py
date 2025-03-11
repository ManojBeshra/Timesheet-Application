from django.db import models
from django.contrib.auth.models import User
from task.models import ticket, priority_type, ticket_type

class worklog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    workdone = models.CharField(max_length=200, null=True, blank=True)
    project_support = models.ForeignKey(ticket_type, on_delete=models.CASCADE, null=True, blank=True, related_name="worklog_project_support")
    ticket = models.ForeignKey(ticket, on_delete=models.CASCADE, null=True, blank=True, related_name="worklog_ticket")
    hours = models.IntegerField(null=True, blank=True)
    billable = models.BooleanField(null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    week = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Worklog - {self.workdone} (User: {self.user})"
    

class requestreview(models.Model):
    send_to = models.ManyToManyField(User, related_name="worklog_send_to")  
    requested_note = models.CharField(max_length=300, null=True, blank=True)
    requested_date = models.DateTimeField(auto_now_add=True)  # Auto add request date




