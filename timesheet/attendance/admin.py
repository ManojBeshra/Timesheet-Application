from django.contrib import admin
from attendance.models import Attendance, AttendanceDetail, LeaveType, LeaveDetails, Approval

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')

class AttendanceDetailAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'entry', 'exit', 'hour', 'note')

class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('id','name')

class LeaveDetailsAdmin(admin.ModelAdmin):
    list_display = ('requested_date', 'type', 'leave_from', 'leave_to', 'approval', 'user')

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceDetail, AttendanceDetailAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(Approval, ApprovalAdmin)
admin.site.register(LeaveDetails, LeaveDetailsAdmin)
