from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #attendance
    path('attendance/', views.attendance_view, name='attendance'),
    path('entry/', views.entry_view, name='entry'),
    path('exit/', views.exit_view, name='exit'),
    #leave details 
    path('leavedetails/',views.leavedetails_view, name='leavedetails'),
    # Add this path for message update
    path('save-note/<int:record_id>/', views.save_note_view, name='save_note'),
    path("delete-attendance/", views.delete_attendance, name="delete_attendance"),
    
]
