from django.shortcuts import render
from .models import ticket, ticket_type, priority_type
from customer.models import customer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def task(request):

    tickets = ticket.objects.all()
    return render(request, 'task.html', {'ticketlist':tickets})

def taskdetails(request):
    return render(request, 'taskdetails.html')

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