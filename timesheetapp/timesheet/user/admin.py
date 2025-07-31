from django.contrib import admin
from django.utils.html import format_html
from .models import ManagerAssignment, Profile, Teams

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'designation', 'wages', 'profile_picture', 'phone', 'address']

class TeamsAdmin(admin.ModelAdmin):
    list_display = ['teamname']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Teams, TeamsAdmin)
admin.site.register(ManagerAssignment)
