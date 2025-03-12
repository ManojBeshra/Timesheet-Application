from django.urls import path
from . import views

urlpatterns = [
    path('worklog/', views.worklog_list, name='worklog'),
    path('worklogdetails/<int:worklog_id>/', views.worklog_details, name='worklogdetails'),
    path("add_worklog/", views.add_worklog, name="add_worklog"),
    path("requestreview_mail/", views.requestreview_mail, name="requestreview_mail"),
    path("export_worklogs_excel/", views.export_worklogs_excel, name="export_worklogs_excel"),


]
