from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import ticket, priority_type, state, task_type
from .forms import TicketForm
from customer.models import customer


# Create your views here.

def task(request):
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


