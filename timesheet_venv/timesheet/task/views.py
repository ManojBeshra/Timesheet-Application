from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ticket, ticket_type, priority_type, state, comment, project, subproject
from customer.models import customer
from .forms import TicketForm, SolutionForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json
from django.utils.timezone import now

# Create your views here.


# @login_required
# def task(request):
#     customers = customer.objects.all()
#     users = User.objects.all()
#     tickettype = ticket_type.objects.all()  
#     priority = priority_type.objects.all()
#     statelist = state.objects.all()
#     tickets = ticket.objects.all()
#     projects = project.objects.all()


#     if not request.user.is_staff:
#         tickets = tickets.filter(assigned_to=request.user)
        
#     return render(request, 'task.html', {
#         'ticketlist':tickets, 
#         'users':users, 
#         'customers': customers, 
#         'tickettype': tickettype, 
#         'priority': priority, 
#         'state': statelist,
#         'projects': projects
#         })



@login_required
@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        try:
            ticket_id = request.POST.get('ticket_id')
            ticket_title = request.POST.get('ticket_title')
            customers = request.POST.get('customerlist')
            ticket_types = request.POST.get('tickettypelist')
            date_opened = request.POST.get('date')
            prioritys = request.POST.get('prioritylist')
            state_id  = request.POST.get('statelist')
            operational_notes = request.POST.get('shortdescriptionarea')
            assigned_users = request.POST.getlist('assigneduserlist[]') # Get multiple users
            projects = request.POST.get('projects')  

            # Fetch objects
            customer_obj = customer.objects.get(id=customers)
            ticket_type_obj = ticket_type.objects.get(id=ticket_types)
            priority_obj = priority_type.objects.get(id=prioritys)
            state_obj = state.objects.get(id=state_id)
            project_obj = project.objects.get(id=projects)

            # Create new ticket
            new_ticket = ticket(
                ticket_id = ticket_id,
                ticket_title=ticket_title,
                customer=customer_obj,
                ticket_type=ticket_type_obj,
                date_opened=date_opened,
                priority=priority_obj,
                state=state_obj,
                operational_notes=operational_notes,
                project = project_obj
            )
            new_ticket.save()

            if project_obj.project_name != "No Project":
                subproject.objects.create(
                sub_project_name=ticket_title,
                project=project_obj,
                date_opened=now().date()
            )
                

            # Assign multiple users
            assigned_user_objs = User.objects.filter(id__in=assigned_users)
            new_ticket.assigned_to.set(assigned_user_objs)  # Use `.set()` for ManyToManyField


         
                

            return JsonResponse({"success": True, "message": "Ticket added successfully!"})
        except Exception as e:
            print(f"Error: {e}")  # Debugging
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


@login_required
def taskdetails(request, ticket_id):
    ticket_instance = get_object_or_404(ticket, pk=ticket_id)

    if request.method == 'POST':
        form1 = TicketForm(request.POST, instance=ticket_instance)

        if form1.is_valid():

            ticket_instance = form1.save(commit=False)
            
            ticket_instance.last_updated = timezone.now()  
            ticket_instance.last_updated_by = request.user  
            ticket_instance.closed_date = timezone.now()

            ticket_instance.save()
            form1.instance.assigned_to.set(request.POST.getlist('assigned_to'))  # Handle ManyToManyField
            return redirect('task')

    else:
        
        form1 = TicketForm(instance=ticket_instance)

    users = User.objects.all()
    customers = customer.objects.all()
    priority_types = priority_type.objects.all()
    states = state.objects.all()
    task_types = ticket_type.objects.all()
    projects = project.objects.all()

    return render(request, 'taskdetails.html', {
        'form1': form1,
        'users': users,
        'ticket': ticket_instance,
        'customers': customers,
        'priority_types': priority_types,
        'states': states,
        'task_types': task_types,
        'projects': projects
    })

@login_required
def filter_tasks(request, user_id=None, project_id=None):
    users = User.objects.all()
    projects = project.objects.all()
    tasks = ticket.objects.all()  

    selected_user = None
    selected_project = None

    # user filter
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        tasks = tasks.filter(assigned_to=selected_user)

    # project filter
    if project_id:
        selected_project = get_object_or_404(project, pk=project_id)
        tasks = tasks.filter(project=selected_project)

    customers = customer.objects.all()
    tickettype = ticket_type.objects.all()
    priority = priority_type.objects.all()
    statelist = state.objects.all()

    return render(request, 'task.html', {
        'ticketlist': tasks, 
        'users': users, 
        'customers': customers, 
        'tickettype': tickettype, 
        'priority': priority, 
        'state': statelist,
        'projects': projects,
        'selected_user': selected_user,
        'selected_project': selected_project,
    })


@login_required
def taskhistory(request):
    users = User.objects.all()
    completed_states = state.objects.filter(state_name__in=["Completed", "Canceled"])

    tasks = ticket.objects.filter(state__in=completed_states)

    return render(request, "taskhistory.html", {"tasks": tasks, "users": users})


@login_required
def filterTaskByUserforHistory(request, id):
    users = User.objects.all()
    selected_user = get_object_or_404(User, pk=id)
    completed_state = get_object_or_404(state, state_name = "Completed")
    tasks = ticket.objects.filter(state = completed_state, assigned_to = selected_user)
    states = state.objects.all()

    return render(request, 'taskhistory.html', {'users': users, "tasks": tasks, 'states': states , 'selected_user': selected_user})



# @login_required
# def filter_taskhistory(request, user_id=None, project_id=None):
#     users = User.objects.all()
#     projects = project.objects.all()

#     completed_states = state.objects.filter(state_name__in=["Completed", "Canceled"])
#     tasks = ticket.objects.filter(state__in=completed_states)

#     selected_user = None
#     selected_project = None

#     # user filter
#     if user_id:
#         selected_user = get_object_or_404(User, pk=user_id)
#         tasks = tasks.filter(assigned_to=selected_user)

#     # project filter
#     if project_id:
#         selected_project = get_object_or_404(project, pk=project_id)
#         tasks = tasks.filter(project=selected_project)

#     customers = customer.objects.all()
#     tickettype = ticket_type.objects.all()
#     priority = priority_type.objects.all()
#     statelist = state.objects.all()

#     return render(request, 'taskhistory.html', {
#         'ticketlist': tasks,
#         'users': users,
#         'customers': customers,
#         'tickettype': tickettype,
#         'priority': priority,
#         'state': statelist,
#         'projects': projects,
#         'selected_user': selected_user,
#         'selected_project': selected_project,
#     })





#for comment
@csrf_exempt  
def add_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ticket_id = data.get("ticket_id")
        text = data.get("text")

        if ticket_id and text:
            ticket_instance = ticket.objects.get(id=ticket_id)
            new_comment = comment.objects.create(
                ticket=ticket_instance,
                user=request.user,
                text=text,
                created_at=now()
            )

            return JsonResponse({
                "success": True,
                "username": request.user.username,
                "text": new_comment.text,
                "created_at": new_comment.created_at.strftime("%b %d, %Y, %I:%M %p")
            })
        return JsonResponse({"success": False, "error": "Invalid data"}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)