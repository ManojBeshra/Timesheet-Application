from django.db import models
from django.contrib.auth.models import User
from task .models import ticket, priority_type, ticket_type



class worklog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(null=True)
    ticket_type = models.ForeignKey(ticket_type, on_delete=models.CASCADE, null=True, related_name="worklog_ticket_type")
    workdone = models.CharField(max_length=200, null=True)
    # project_support = models.ForeignKey(project, on_delete=models.CASCADE, null=True, related_name="worklog_project_support")
    ticket = models.ForeignKey(ticket, on_delete=models.CASCADE, null=True, related_name="worklog_ticket")
    hours = models.IntegerField(null=True)
    billable = models.BooleanField(null=True)
    note = models.CharField(max_length=200, default="", null=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null = True)
    category = models.CharField(max_length=100, null=True)
    week = models.CharField(max_length=100, null=False)