from django.shortcuts import render
from .models import ticket

# Create your views here.

def task(request):
    return render(request, 'task.html')

def taskdetails(request):
    return render(request, 'taskdetails.html')

def add_task(request):
    if request.method == 'POST':
        ticket_name = request.POST.get('title')
        customer = request.POST.get('customer')
        short_description = request.POST.get('short_description')
        ticket_type = request.POST.get('ticket_type')
        date_opened = request.POST.get('date_opened')
        assigned_user = request.POST.get('assigned_user')
        priority = request.POST.get('priority')
        comments = request.POST.get('comments')

        # Create and save the new task
        ticket = ticket(
            ticket_name=ticket_name,
            customer=customer,
            short_description=short_description,
            task_type=task_type,
            assigned_user=assigned_user,
            priority=priority,
            comments=comments,
        )
        ticket.save()
        return redirect('taskdetails', task_id=task.id)
    return render(request, 'task.html')