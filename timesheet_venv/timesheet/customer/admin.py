from django.contrib import admin
from .models import customer, customer_contact

# Register your models here.
class customerAdmin(admin.ModelAdmin):
    list_display =['name', 'company']

class customerContactAdmin(admin.ModelAdmin):
    list_display = ['customer', 'contact_id']
admin.site.register(customer_contact)
admin.site.register(customer, customerAdmin)