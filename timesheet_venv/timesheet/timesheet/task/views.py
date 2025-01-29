from django.shortcuts import render, redirect, get_object_or_404
from .models import ticket, ticket_type, priority_type, state
from customer.models import customer
from .forms import TicketForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def task(request):
    customers = customer.objects.all()
    users = User.objects.all()
    tickettype = ticket_type.objects.all()  
    priority = priority_type.objects.all()

    tickets = ticket.objects.all()
    return render(request, 'task.html', {'ticketlist':tickets, 'users':users, 'customers': customers, 'tickettype': tickettype, 'priority': priority})

# def taskdetails(request):
#     return render(request, 'taskdetails.html')

@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        ticket_name = request.POST.get('title')
        print(ticket_name)
        customers = request.POST.get('customerlist')
        short_description = request.POST.get('shortdescriptionarea')
        ticket_types = request.POST.get('tickettypelist')
        date_opened = request.POST.get('date')
        assigned_users = request.POST.get('assigneduserlist')
        prioritys = request.POST.get('prioritylist')
        comments = request.POST.get('commentsarea')

        # Create and save the new task
        tickets = ticket(
            ticket_name=ticket_name,
            customer=customer.objects.get(name='IMC'),
            short_description=short_description,
            ticket_type=ticket_type.objects.get(id=1),
            assigned_to=User.objects.get( id = 1),
            priority=priority_type.objects.get(id=1),
            comments=comments,
        )
        tickets.save()

       
    return render(request, 'task.html')









# def task(request):
#     users = User.objects.all() 
#     tasks = ticket.objects.all()  
#     states = state.objects.all()
#     customers = customer.objects.all()
#     return render(request, 'task2.html', {'users': users, 'tasks': tasks, 'customers': customers, 'states': states})
    


def filterTaskByUser(request, id):
    users = User.objects.all()
    user = get_object_or_404(User, pk=id) 
    tasks = ticket.objects.filter(assigned_to=user)  
    states = state.objects.all()
    return render(request, 'task.html', {'users': users, 'ticketlist': tasks, 'states': states})




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