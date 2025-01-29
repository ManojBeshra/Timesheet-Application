from django.urls import path
from . import views

urlpatterns = [
    #task
    path('task/',views.task, name='task'),
<<<<<<< HEAD
    path('task/filter/<int:id>/', views.filterTaskByUser, name='filterTaskByUser'),
    path('taskdetails/<int:ticket_id>',views.taskdetails, name='taskdetails'),
=======
    path('taskdetails/',views.taskdetails, name='taskdetails'),
    path('add/',views.add_task, name='add_task'),
>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2
]



