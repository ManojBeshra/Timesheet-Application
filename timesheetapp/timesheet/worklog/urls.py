from django.urls import path
from . import views
from .views import mark_notifications_seen


urlpatterns = [
    path('worklog/', views.worklog_list, name='worklog'),
    path('worklogdetails/<int:worklog_id>/', views.worklog_details, name='worklogdetails'),
    path("add_worklog/", views.add_worklog, name="add_worklog"),
    path("requestreview_mail/", views.requestreview_mail, name="requestreview_mail"),
    # path("export_worklogs_excel/", views.export_worklogs_excel, name="export_worklogs_excel"),
    path("export_worklogs_csv/", views.export_worklogs_csv, name="export_worklogs_csv"),
    path('delete-worklog/', views.delete_worklog, name='delete_worklog'),
    path('notifications/mark-seen/', views.mark_notifications_seen, name='mark_notifications_seen'),


]

