from django.urls import path
from . import views

urlpatterns = [
    path('worklog/', views.worklog_list, name='worklog'),
    path('worklogdetails/<int:worklog_id>/', views.worklog_details, name='worklogdetails'),

    path("add_worklog/", views.add_worklog, name="add_worklog"),
    path("requestreview_mail/", views.requestreview_mail, name="requestreview_mail"),

]
