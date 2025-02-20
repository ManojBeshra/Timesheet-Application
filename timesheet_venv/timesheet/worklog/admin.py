from django.contrib import admin
from .models import worklog

# Register your models here.
# Register your models here.
class worklog_admin(admin.ModelAdmin):
    list_display = ['user', 'date', 'ticket_type', 'workdone', 'ticket', 'hours', 'billable', 'note', 'priority', 'category', 'week']

admin.site.register(worklog, worklog_admin)