from django.contrib import admin
from django.utils.html import format_html
from .models import ManagerAssignment, Profile, Teams

class TeamsAdmin(admin.ModelAdmin):
    list_display = ['teamname']

# admin.py
admin.site.register(ManagerAssignment)
admin.site.register(Teams, TeamsAdmin)
admin.site.register(Profile)