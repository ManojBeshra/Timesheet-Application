from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('userdetails/', views.userdetails, name='userdetails'),
    path('teamdetail/', views.teamdetail, name='teamdetail'),
]