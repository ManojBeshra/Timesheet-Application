from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class AttendanceReport(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.IntegerField(default=datetime.datetime.now().year)
    month = models.IntegerField(choices=MONTH_CHOICES)
    total_present_days = models.PositiveIntegerField(default=0)
    total_absent_days = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.AttendanceReport.name} - {self.get_month_display()} {self.year}"

class ProjectReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    billable_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    non_billable_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def total_hours(self):
        return self.billable_hours + self.non_billable_hours