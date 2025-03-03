from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import worklog
from task . models import ticket, priority_type, ticket_type
from .forms import WorklogForm
from django.contrib.auth.models import User
import json
from django.utils import timezone


def worklog_list(request): 
    worklogs = worklog.objects.all()  
    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    tickettype = ticket_type.objects.all()

    return render(request, 'worklog.html', {
        'worklogs': worklogs,
        'priority': priority,
        'tickets': tickets,
        'users': users,
        'tickettype': tickettype,
    })


@csrf_exempt  
def add_worklog(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Create a new worklog entry
        worklog_instance = worklog.objects.create(
            user=request.user,  
            workdone=data.get("workdone"),
            hours=data.get("hours"),
            ticket_id=data.get("ticket"),
            date=data.get("date"),
            week=data.get("week"),
            priority_id=data.get("priority"),
            project_support_id=data.get("project_support"),
            category=data.get("category"),
            note=data.get("note"),
            billable=data.get("billable"),
        )
        
        # Return a success message or the created worklog object
        return JsonResponse({"message": "Log added successfully!", "status": "success"})
    
    return JsonResponse({"message": "Invalid method", "status": "error"})

