from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #attendance
    path('attendance/', views.attendance_view, name='attendance'),
    path('entry/', views.entry_view, name='entry'),
    path('exit/', views.exit_view, name='exit'),
    
    # Add this path for message update
    path('save-note/<int:record_id>/', views.save_note_view, name='save_note'),
    
 # pto
 #leave details 
    path('leavedetails/',views.leavedetails_view, name='leavedetails'),
    path('add-leave/', views.add_leave_details, name='add_leave'),
    
    path('approve-leave/', views.approve_leave, name='approve_leave'),

]
