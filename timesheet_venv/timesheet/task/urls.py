from django.urls import path
from . import views

urlpatterns = [
    #task
    path('task/',views.task, name='task'),
    path('taskdetails/',views.taskdetails, name='taskdetails'),
    path('add/',views.add_task, name='add_task'),
]
