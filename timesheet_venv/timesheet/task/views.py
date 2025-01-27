from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import ticket

# Create your views here.

def task(request):
    users = User.objects.all() 
    tasks = ticket.objects.all()  
    return render(request, 'task.html', {'users': users, 'tasks': tasks})
    


def filterTaskByUser(request, id):
    users = User.objects.all()
    user = get_object_or_404(User, pk=id) 
    tasks = ticket.objects.filter(assigned_to=user)  
    return render(request, 'task.html', {'users': users, 'tasks': tasks})
