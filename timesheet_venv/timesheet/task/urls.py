from django.urls import path
from . import views

urlpatterns = [
    #task
    path('taskdetails/<int:ticket_id>',views.taskdetails, name='taskdetails'),
    path('add/',views.add_task, name='add_task'),
    # path('taskhistory/', views.taskhistory, name ="taskhistory"),
    # path('taskhistory/filter/<int:id>/', views.filterTaskByUserforHistory, name = "filterTaskByUserforHistory"),
    path('add-comment/', views.add_comment, name="add_comment"),

    path("task/", views.filter_tasks, name="task"),  # Default task list
    path("task/filter/user/<int:user_id>/", views.filter_tasks, name="filterTaskByUser"),
    path("task/filter/project/<int:project_id>/", views.filter_tasks, name="filterTaskByProject"),
    path("task/filter/user/<int:user_id>/project/<int:project_id>/", views.filter_tasks, name="filterTaskByUserAndProject"),


    path("taskhistory/", views.filter_taskhistory, name="taskhistory"),  # Default taskhistory list
    path("taskhistory/filter/user/<int:user_id>/", views.filter_taskhistory, name="filterTaskhistoryByUser"),
    path("taskhistory/filter/project/<int:project_id>/", views.filter_taskhistory, name="filterTaskhistoryByProject"),
    path("taskhistory/filter/user/<int:user_id>/project/<int:project_id>/", views.filter_taskhistory, name="filterTaskhistoryByUserAndProject"),


]
