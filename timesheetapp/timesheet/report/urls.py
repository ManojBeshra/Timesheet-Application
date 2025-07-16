from django.urls import path
from . import views

urlpatterns = [
    #attendance
    path('report/', views.landingpage, name='report'),
    #logreport
    path('logreport/', views.logreport_view, name='logreport'),
    # path('project-details-report/', views.projectdetailsreport, name='projectdetailsreport'),
    path('projectdetailsreport/<int:ticket_id>/', views.projectdetailsreport, name='projectdetailsreport'),
    path('download/', views.download_report, name='download_report'),
    path('download-pro-report/', views.download_pro_report, name='download_pro_report'),
    path ('test/', views.attendancereport_view, name = "test" )

]
