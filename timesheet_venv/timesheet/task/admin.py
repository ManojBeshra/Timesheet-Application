from django.contrib import admin
from .models import ticket, ticket_detail, ticket_type, priority_type, state

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']

class ticket_admin(admin.ModelAdmin):
    list_display = ['ticket_name','customer','ticket_type','date_opened','priority', 'assigned_to','last_updated','short_description','comments','user_comments']

class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']

class ticket_type_admin(admin.ModelAdmin):
    list_display = ['id', 'name']

class ticket_detail_admin(admin.ModelAdmin):
    list_display = ['id', 'ticket','date','user','detail', ]

admin.site.register(ticket_type, ticket_type_admin)
admin.site.register(ticket,ticket_admin)
admin.site.register(ticket_detail, ticket_detail_admin)
admin.site.register(priority_type, priority_admin) 
admin.site.register(state, state_admin)


