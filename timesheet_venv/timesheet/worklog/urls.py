from django.urls import path
from . import views

urlpatterns = [
    path('worklog/', views.worklog_list, name='worklog'),
    path("add_worklog/", views.add_worklog, name="add_worklog"),
]
