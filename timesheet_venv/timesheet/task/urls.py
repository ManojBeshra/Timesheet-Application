from django.urls import path
from . import views

urlpatterns = [
    #task
    path('task/',views.task, name='task'),
    path('task/filter/<int:id>/', views.filterTaskByUser, name='filterTaskByUser'),
    path('taskdetails/<int:ticket_id>',views.taskdetails, name='taskdetails'),
]



