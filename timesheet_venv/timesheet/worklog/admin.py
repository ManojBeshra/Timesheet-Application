from django.contrib import admin
from .models import worklog

# Register your models here.
class worklog_admin(admin.ModelAdmin):
    list_display = ['user', 'date','workdone', 'project_support', 'ticket', 'hours', 'billable', 'note', 'priority', 'category', 'week']
    
admin.site.register(worklog, worklog_admin)
