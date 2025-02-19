from django.shortcuts import render
from task.models import priority_type, ticket
from project.models import project
from django.contrib.auth.models import User


# Create your views here.

def worklog(request):

    priority = priority_type.objects.all()
    users = User.objects.all()
    projects = project.objects.all()
    tickets = ticket.objects.all()
    return render(request, 'worklog.html', {'priority': priority, 'projects' : projects, 'tickets': tickets, 'users': users})