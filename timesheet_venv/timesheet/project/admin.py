from django.contrib import admin
from .models import project
from django.utils.html import format_html

# Register your models here.

class project_admin(admin.ModelAdmin):
    list_display = [ 'project_id', 'name','customer','estimated_hr','completed_hr','manager', 'get_assigned_users','date', 'estimated_complete_date', 'actual_complete_date']

    def get_assigned_users(self, obj):
        return format_html("<br>".join([user.username for user in obj.assigned_to.all()]))  # Get all assigned users
    
    get_assigned_users.short_description = "Assigned Users"  # Column name in Admin Panel


admin.site.register(project,project_admin)
