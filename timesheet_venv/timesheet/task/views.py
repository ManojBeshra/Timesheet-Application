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
    # for t in tickets:
    #     print(f"Ticket Title: {t.ticket_title}")  # Ensure ticket_title is populated
    return render(request, 'task.html', {
        'ticketlist':tickets, 
        'users':users, 
        'customers': customers, 
        'tickettype': tickettype, 
        'priority': priority, 
        'state': statelist
        })

@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        try:
            ticket_id = request.POST.get('ticket_id')
            ticket_title = request.POST.get('ticket_title')
            #ticket_title = request.POST.get('ticket_title') 
            #print(f"Ticket Title2: {ticket_title}")
            customers = request.POST.get('customerlist')
            ticket_types = request.POST.get('tickettypelist')
            date_opened = request.POST.get('date')
            prioritys = request.POST.get('prioritylist')
            state_id  = request.POST.get('statelist')
            short_description = request.POST.get('shortdescriptionarea')
            assigned_users = request.POST.getlist('assigneduserlist[]')  # Get multiple users

            # Fetch objects
            customer_obj = customer.objects.get(id=customers)
            ticket_type_obj = ticket_type.objects.get(id=ticket_types)
            priority_obj = priority_type.objects.get(id=prioritys)
            state_obj = state.objects.get(id=state_id)

            # Create new ticket
            new_ticket = ticket(
                ticket_id = ticket_id,
                ticket_title=ticket_title,
                customer=customer_obj,
                ticket_type=ticket_type_obj,
                date_opened=date_opened,
                priority=priority_obj,
                state=state_obj,
                short_description=short_description,
            )
            new_ticket.save()

            # Assign multiple users
            assigned_user_objs = User.objects.filter(id__in=assigned_users)
            new_ticket.assigned_to.set(assigned_user_objs)  # Use `.set()` for ManyToManyField

            return JsonResponse({"success": True, "message": "Ticket added successfully!"})
        except Exception as e:
            print(f"Error: {e}")  # Debugging
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


#working
def taskdetails(request, ticket_id):
    ticket_instance = get_object_or_404(ticket, pk=ticket_id)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket_instance)

        if form.is_valid():
            form.save()
            form.instance.assigned_to.set(request.POST.getlist('assigned_to'))  # Handle ManyToManyField
            return redirect('task')

    else:
        form = TicketForm(instance=ticket_instance)

    users = User.objects.all()
    customers = customer.objects.all()
    priority_types = priority_type.objects.all()
    states = state.objects.all()
    task_types = ticket_type.objects.all()

    return render(request, 'taskdetails.html', {
        'form': form,
        'users': users,
        'ticket': ticket_instance,
        'customers': customers,
        'priority_types': priority_types,
        'states': states,
        'task_types': task_types
    })



def filterTaskByUser(request, id):
    users = User.objects.all()
    tasks = ticket.objects.all()
    states = state.objects.all()
    selected_user = get_object_or_404(User, pk=id)
    tasks = tasks.filter(assigned_to=selected_user)
    
    return render(request, 'task.html', {'users': users, 'ticketlist': tasks, 'states': states, 'selected_user': selected_user})

def taskhistory(request):
    users = User.objects.all()
    completed_state = get_object_or_404(state, state_name = "Completed")
    tasks = ticket.objects.filter(state = completed_state)

    return render(request, "taskhistory.html", {"tasks": tasks, "users": users})

def filterTaskByUserforHistory(request, id):
    users = User.objects.all()
    selected_user = get_object_or_404(User, pk=id)
    completed_state = get_object_or_404(state, state_name = "Completed")
    tasks = ticket.objects.filter(state = completed_state, assigned_to = selected_user)
    states = state.objects.all()


    return render(request, 'taskhistory.html', {'users': users, "tasks": tasks, 'states': states , 'selected_user': selected_user})