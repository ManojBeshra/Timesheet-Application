from django.contrib import admin
from .models import company
# Register your models here.

class companyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
admin.site.register(company, companyAdmin)