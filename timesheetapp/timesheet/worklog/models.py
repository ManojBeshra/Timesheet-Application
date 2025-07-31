from django.db import models
from django.contrib.auth.models import User
from task.models import ticket, priority_type, ticket_type

class status(models.Model):
   status = models.CharField(max_length=100)
   def __str__(self):
        return f"{self.status}"
   
def get_default_status():
    return status.objects.get(status="Request Review").id


class worklog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    workdone = models.CharField(max_length=1500, null=True, blank=True)
    project_support = models.ForeignKey(ticket_type, on_delete=models.CASCADE, null=True, blank=True, related_name="worklog_project_support")
    ticket = models.ForeignKey(ticket, on_delete=models.CASCADE, null=True, blank=True, related_name="worklog_ticket")
    hours = models.IntegerField(null=True, blank=True)
    billable = models.BooleanField(null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    week = models.CharField(max_length=100, blank=True)
    status = models.ForeignKey(status, on_delete=models.CASCADE, default=get_default_status)


    def __str__(self):
        return f"Worklog - {self.workdone} (User: {self.user})"
    

class requestreview(models.Model):
    send_to = models.ManyToManyField(User, related_name="worklog_send_to")  
    requested_note = models.CharField(max_length=300, null=True, blank=True)
    requested_date = models.DateTimeField(auto_now_add=True)  # Auto add request date



class MailNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    week_start_date = models.DateField(null=False)
    notification_seen = models.BooleanField(default=False)  
    def __str__(self):
        return f"Notification for {self.user} on {self.created_at}"
