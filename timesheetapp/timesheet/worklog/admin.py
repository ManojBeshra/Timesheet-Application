from django.contrib import admin
from .models import worklog, requestreview, status

# Register your models here.

class status_admin(admin.ModelAdmin):
    list_display = ['id', 'status']


class worklog_admin(admin.ModelAdmin):
    list_display = ['user', 'date','workdone', 'project_support', 'ticket', 'hours', 'billable', 'note', 'priority', 'category', 'week']


class requestreview_admin(admin.ModelAdmin):
    list_display = ["get_assigned_users", "requested_note", "requested_date"]

    def get_assigned_users(self, obj):
        return ", ".join([user.username for user in obj.send_to.all()])  

    get_assigned_users.short_description = "Assigned Users"

admin.site.register(requestreview, requestreview_admin)
admin.site.register(worklog, worklog_admin)
admin.site.register(status, status_admin)