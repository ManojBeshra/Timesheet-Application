from django.urls import path
from . import views

urlpatterns = [
    path('worklog/', views.worklog_list, name='worklog'),
    path("add_worklog/", views.add_worklog, name="add_worklog"),
    path('worklog/filter/user/<int:user_id>/', views.filter_worklog, name='filterWorklogByUser'),
    path('worklog/filter/billable/<str:billable_status>/', views.filter_worklog, name='filterWorklogByBillable'),
    path('filter/user/<int:user_id>/billable/<str:billable_status>/', views.filter_worklog, name='filterWorklogByUserAndBillable'),
    path("requestreview_mail/", views.requestreview_mail, name="requestreview_mail"),

]
