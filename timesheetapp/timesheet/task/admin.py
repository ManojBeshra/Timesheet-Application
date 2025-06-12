from django.contrib import admin
from .models import ticket, ticket_type, priority_type, state, comment, project, subproject
from django.utils.html import format_html

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']

class ticket_admin(admin.ModelAdmin):
    list_display = ['ticket_id', 'ticket_title','customer','ticket_type','date_opened','priority', 'get_assigned_users','last_updated', 'last_updated_by', 'state', 'operational_notes','closed_date','solution']

    def get_assigned_users(self, obj):
        return format_html("<br>".join([user.username for user in obj.assigned_to.all()]))  # Get all assigned users
    
    get_assigned_users.short_description = "Assigned Users"  # Column name in Admin Panel


class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']

class ticket_type_admin(admin.ModelAdmin):
    list_display = ['id', 'name']

# class ticket_update_history_admin(admin.ModelAdmin):
#     list_display = ['id', 'updated_on','updated_by','changes']

class comment_admin(admin.ModelAdmin):
    list_display = ['ticket','user','text', 'created_at']

class project_admin(admin.ModelAdmin):
    list_display = ['project_id','project_name']

class sub_project_admin(admin.ModelAdmin):
    list_display = ['sub_project_name', 'date_opened']

admin.site.register(ticket_type, ticket_type_admin)
admin.site.register(ticket,ticket_admin)
# admin.site.register(ticket_update_history, ticket_update_history_admin)
admin.site.register(priority_type, priority_admin) 
admin.site.register(state, state_admin)
admin.site.register(comment, comment_admin)
admin.site.register(project,project_admin)
admin.site.register(subproject, sub_project_admin)

