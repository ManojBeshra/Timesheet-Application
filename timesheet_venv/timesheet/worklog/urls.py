from django.urls import path
from . import views

urlpatterns = [
    path('worklog/',views.worklog, name='worklog')
]