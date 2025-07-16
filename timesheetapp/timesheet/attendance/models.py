from django.db import models
from django.contrib.auth.models import User 
from datetime import datetime
from django.utils import timezone
from datetime import date


# Create your models here.

#Attendance Details
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class AttendanceDetail(models.Model):
    attendance = models.ForeignKey(Attendance, related_name='details', on_delete=models.CASCADE)
    entry = models.TimeField(null=True, blank=True)
    exit = models.TimeField(null=True, blank=True)
    hour = models.IntegerField(default=0)
    note = models.TextField(default="")

    def save(self, *args, **kwargs):
        if self.entry and self.exit:
            self.hour = int((datetime.combine(datetime.today(), self.exit) - datetime.combine(datetime.today(), self.entry)).total_seconds())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attendance.user.username} - {self.attendance.date} - Entry: {self.entry.strftime('%I:%M %p') if self.entry else 'N/A'} - Exit: {self.exit.strftime('%I:%M %p') if self.exit else 'N/A'}"

    def duration(self):
        return f"{self.hour // 3600} hr {(self.hour % 3600) // 60} min {self.hour % 60} sec" if self.hour else 'N/A'


#Leave Details
class LeaveType(models.Model):
    name = models.CharField(max_length=30, null=True, default=None)

    def __str__(self):
        return self.name
    
class Approval(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):  
        return self.name

class LeaveDetails(models.Model):
    requested_date = models.DateField(auto_now_add=True)
    type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True)
    leave_from = models.DateField(null=True)
    leave_to = models.DateField(null=True)
    approval = models.ForeignKey(Approval, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="RequestedUser")
    description = models.TextField(default = "")
    remarks = models.TextField(default="")
    approvedby = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, blank= True, related_name="ApprovedBy")

class userLeaveDays(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True)
    leaveTaken = models.IntegerField(default=0) 
    def __str__(self):
        return f"{self.user} - {self.type} : {self.leaveTaken} days taken"




class EarnedLeaveDay(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_date = models.DateField(default=timezone.now)
    last_updated = models.DateField(auto_now=True)
    earned_leave_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.earned_leave_days} days"

    def calculate_earned_leave(self):
        join_date = self.joined_date  
        today = self.last_updated 
       
        total_years = (today - join_date).days / 365.25  

        if total_years <= 3:
            return 10
        elif 3 < total_years < 5:
            return 13
        else:
            return 16
