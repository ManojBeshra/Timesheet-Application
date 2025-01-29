from django.urls import path
from . import views

urlpatterns = [
    #task
    path('task/',views.task, name='task'),
    path('taskdetails/<int:ticket_id>',views.taskdetails, name='taskdetails'),
    path('task/filter/<int:id>/', views.filterTaskByUser, name='filterTaskByUser'),
    path('add/',views.add_task, name='add_task'),
]
