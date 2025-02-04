from django.shortcuts import render, redirect, get_object_or_404
from .models import ticket, ticket_type, priority_type, state
from customer.models import customer
from .forms import TicketForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

# Create your views here.

def task(request):
    customers = customer.objects.all()
    users = User.objects.all()
    tickettype = ticket_type.objects.all()  
    priority = priority_type.objects.all()
    statelist = state.objects.all()

    tickets = ticket.objects.all()
    return render(request, 'task.html', {'ticketlist':tickets, 'users':users, 'customers': customers, 'tickettype': tickettype, 'priority': priority, 'state': statelist})


#working on
@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        ticket_name = request.POST.get('title')
        customers = request.POST.get('customerlist')
        short_description = request.POST.get('shortdescriptionarea')
        ticket_types = request.POST.get('tickettypelist')
        date_opened = request.POST.get('date')
        assigned_users = request.POST.get('assigneduserlist')
        state_id  = request.POST.get('statelist')
        prioritys = request.POST.get('prioritylist')
        comments = request.POST.get('commentsarea')

        try:
            # Ensure valid object references exist
            customer_obj = customer.objects.get(id=customers)
            ticket_type_obj = ticket_type.objects.get(id=ticket_types)
            assigned_user_obj = User.objects.get(id=assigned_users)
            priority_obj = priority_type.objects.get(id=prioritys)
            state_obj = state.objects.get(id=state_id )

            # Create and save the new task
            new_ticket = ticket(
                ticket_name=ticket_name,
                customer=customer_obj,
                short_description=short_description,
                ticket_type=ticket_type_obj,
                assigned_to=assigned_user_obj,
                state=state_obj,
                priority=priority_obj,
                comments=comments,
                date_opened=date_opened
            )
            new_ticket.save()

            return JsonResponse({"success": True, "message": "Task added successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



def taskdetails(request, ticket_id):
    ticket_instance = get_object_or_404(ticket, pk=ticket_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket_instance)
        if form.is_valid():
            form.save()
            return redirect('task')  
 
    else:
        form = TicketForm(instance=ticket_instance)  

    users = User.objects.all()
    customers = customer.objects.all()
    priority_types = priority_type.objects.all()
    states = state.objects.all()
    task_types = ticket_type.objects.all()
    return render(request, 'taskdetails.html', {'form': form, 'users': users,  'ticket': ticket_instance, 'customers': customers, 'priority_types':priority_types, 'states': states, 'task_types': task_types})



def filterTaskByUser(request, id):
    users = User.objects.all()
    user = get_object_or_404(User, pk=id) 
    tasks = ticket.objects.filter(assigned_to=user)  
    states = state.objects.all()
    return render(request, 'task.html', {'users': users, 'ticketlist': tasks, 'states': states})




def taskhistory(request):
    users = User.objects.all()
    completed_state = get_object_or_404(state, state_name = "Completed")
    tasks = ticket.objects.filter(state = completed_state)

    return render(request, "taskhistory.html", {"tasks": tasks, "users": users})




def filterTaskByUserforHistory(request, id):
    users = User.objects.all()
    user = get_object_or_404(User, pk=id) 
    completed_state = get_object_or_404(state, state_name = "Completed")
    tasks = ticket.objects.filter(state = completed_state, assigned_to = user)
    states = state.objects.all()
    return render(request, 'taskhistory.html', {'users': users, "tasks": tasks, 'states': states})