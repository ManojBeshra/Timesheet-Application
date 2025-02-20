from django.shortcuts import render
from task.models import priority_type, ticket

from django.contrib.auth.models import User


# Create your views here.

def worklog(request):

    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    return render(request, 'worklog.html', {'priority': priority, 'tickets': tickets, 'users': users})