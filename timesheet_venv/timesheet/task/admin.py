from django.contrib import admin
<<<<<<< HEAD
from .models import ticket, ticket_detail, task_type, priority_type, state
=======
from .models import ticket, ticket_detail, ticket_type, priority_type, state
>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2

# Register your models here.
class priority_admin(admin.ModelAdmin):
    list_display = ['id', 'priority_name']

<<<<<<< HEAD
class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']
=======
class ticket_admin(admin.ModelAdmin):
    list_display = ['ticket_name','customer','ticket_type','date_opened','priority', 'assigned_to','last_updated','short_description','comments','user_comments']
>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2

class state_admin(admin.ModelAdmin):
    list_display = ['id', 'state_name']

admin.site.register(ticket_type)
admin.site.register(ticket,ticket_admin)
admin.site.register(ticket_detail)
admin.site.register(priority_type, priority_admin) 
<<<<<<< HEAD
admin.site.register(state, state_admin)
=======
admin.site.register(state,state_admin)


>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2
