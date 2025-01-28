from django.contrib import admin
from .models import ticket, ticket_detail, task_type, priority_type

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']


admin.site.register(task_type)
admin.site.register(ticket)
admin.site.register(ticket_detail)
admin.site.register(priority_type, priority_admin) 


