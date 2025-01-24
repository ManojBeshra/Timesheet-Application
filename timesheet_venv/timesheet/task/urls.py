from django.urls import path
from . import views

urlpatterns = [
    #task
    path('task/',views.task, name='task')
]
