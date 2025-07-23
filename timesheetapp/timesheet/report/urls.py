from django.urls import path
from . import views

urlpatterns = [
    #attendance report
    path('', views.report_redirect_view, name='report_redirect'),  # Main entry point
    path('admin-attendance-report/', views.adminattendancereport_view, name='adminattendancereport'),  
    path('user-attendance-report/', views.userattendancereport_view, name='userattendancereport'),  
    path('download-adminattendancereport/', views.downloadadminattendancereport_view, name='downloadadminattendancereport'),  
    #log report
    path('logreport/', views.logreport_view, name='logreport'),
    path('projectdetailsreport/<int:ticket_id>/', views.projectdetailsreport, name='projectdetailsreport'),
    # path('download/', views.download_report, name='download_report'),
    path('download-pro-report/', views.download_pro_report, name='download_pro_report'),

]
