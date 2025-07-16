from django.contrib import admin
from django.utils.html import format_html
from .models import ManagerAssignment, Profile, Teams

# admin.py
admin.site.register(ManagerAssignment)
admin.site.register(Teams)
admin.site.register(Profile)