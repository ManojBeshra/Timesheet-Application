from django.contrib import admin
from .models import ticket, ticket_update_history, ticket_type, priority_type, state

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']

class ticket_admin(admin.ModelAdmin):
    list_display = ['ticket_title','customer','ticket_type','date_opened','priority', 'assigned_to','last_updated', 'last_updated_by', 'state', 'short_description','closed_date','solution']

class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']

class ticket_type_admin(admin.ModelAdmin):
    list_display = ['id', 'name']

class ticket_update_history_admin(admin.ModelAdmin):
    list_display = ['id', 'updated_on','updated_by','changes']

admin.site.register(ticket_type, ticket_type_admin)
admin.site.register(ticket,ticket_admin)
admin.site.register(ticket_update_history, ticket_update_history_admin)
admin.site.register(priority_type, priority_admin) 
admin.site.register(state, state_admin)


