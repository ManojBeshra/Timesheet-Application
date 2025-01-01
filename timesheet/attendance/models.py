from django.db import models
from django.contrib.auth.models import User 
# Create your models here.

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

    def __str__(self):
        return f"{self.attendance.user.username} - {self.attendance.date} - {self.entry} - {self.exit}"
