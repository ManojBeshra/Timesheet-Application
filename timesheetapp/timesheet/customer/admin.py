from django.contrib import admin
from .models import customer, customer_contact, customer_status

# Register your models here.
class customerAdmin(admin.ModelAdmin):
    list_display =['name','city' ]

class customerContactAdmin(admin.ModelAdmin):
    list_display = ['customer', 'contact_id']

class customerStatusAdmin(admin.ModelAdmin): 
    list_display = ['id', 'status_name']
    
admin.site.register(customer_contact)
admin.site.register(customer, customerAdmin)
admin.site.register(customer_status, customerStatusAdmin)