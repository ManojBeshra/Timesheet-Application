from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import worklog
from task . models import ticket, priority_type, ticket_type
from .forms import WorklogForm
from django.contrib.auth.models import User
import json
from django.utils import timezone
from django.shortcuts import render, get_object_or_404 
from django.contrib import messages  # Import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms import RequestreviewForm
from django.conf import settings

@login_required
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
@login_required
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


    
@csrf_exempt
@login_required
def filter_worklog(request, user_id=None, billable_status=None):
    users = User.objects.all()
    
    # Initialize worklogs
    worklogs = worklog.objects.all()

    selected_user = None
    selected_billable_status = None

    # Filter by user if user_id is provided
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        worklogs = worklogs.filter(user=selected_user)

    # Filter by billable status if billable_status is provided
    if billable_status:
        is_billable = True if billable_status == 'billable' else False
        worklogs = worklogs.filter(billable=is_billable)

    return render(request, 'worklog.html', {
        'worklogs': worklogs,
        'users': users,
        'selected_user': selected_user,
        'billable_status': billable_status
    })
    


@login_required
def requestreview_mail(request):
    if request.method == "POST":
        form = RequestreviewForm(request.POST)
        if form.is_valid():
            request_review = form.save(commit=False)
            request_review.save()
            form.save_m2m()  # Save ManyToMany field after saving instance
            
            recipients = [user.email for user in request_review.send_to.all() if user.email]

            if recipients:
                try:
                    send_mail(
                        subject="Worklog Review Request",
                        message=f"{request_review.requested_note}\n\nhttp://127.0.0.1:5000/worklog/worklog/",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=recipients,
                        fail_silently=False,
                    )
                    messages.success(request, "Email sent successfully!") 
                except Exception as e:
                    messages.error(request, f"Error sending email: {e}")  

            return redirect("worklog")  

    else:
        form = RequestreviewForm()

    return render(request, "worklog.html", {"form": form})



