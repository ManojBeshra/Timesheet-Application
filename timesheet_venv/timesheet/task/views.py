<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import ticket, priority_type, state, task_type
from .forms import TicketForm
from customer.models import customer

=======
from django.shortcuts import render
from .models import ticket, ticket_type, priority_type
from customer.models import customer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2

# Create your views here.

def task(request):
<<<<<<< HEAD
    users = User.objects.all() 
    tasks = ticket.objects.all()  
    states = state.objects.all()
    customers = customer.objects.all()
    return render(request, 'task2.html', {'users': users, 'tasks': tasks, 'customers': customers, 'states': states})
    


def filterTaskByUser(request, id):
    users = User.objects.all()
    user = get_object_or_404(User, pk=id) 
    tasks = ticket.objects.filter(assigned_to=user)  
    states = state.objects.all()
    return render(request, 'task2.html', {'users': users, 'tasks': tasks, 'states': states})




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
    task_types = task_type.objects.all()
    return render(request, 'taskdetails.html', {'form': form, 'users': users,  'ticket': ticket_instance, 'customers': customers, 'priority_types':priority_types, 'states': states, 'task_types': task_types})
=======

    tickets = ticket.objects.all()
    return render(request, 'task.html', {'ticketlist':tickets})
>>>>>>> 8f95ff82a44f516a4511ed59abcd22c373fbcee2


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

        # ticket.objects.create(
             
        #     ticket_name=ticket_name,
        #     customer=customer,
        #     short_description=short_description,
        #     task_type=task_type,
        #     assigned_user=assigned_user,
        #     priority=priority,
        #     comments=comments,
        # )

        # queryset = ticket.objects.all()


    return render(request, 'task.html')