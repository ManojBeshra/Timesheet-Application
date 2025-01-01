from django.contrib import admin
from attendance.models import Attendance, AttendanceDetail

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')

class AttendanceDetailAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'entry', 'exit', 'hour', 'note')

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceDetail, AttendanceDetailAdmin)
