from django.contrib import admin
from .models import ticket, ticket_detail, task_type, priority_type, state

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']

class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']

admin.site.register(task_type)
admin.site.register(ticket)
admin.site.register(ticket_detail)
admin.site.register(priority_type, priority_admin) 
admin.site.register(state, state_admin)
