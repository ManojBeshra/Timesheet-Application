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
from datetime import datetime
from django.db.models.functions import ExtractYear

@login_required
def worklog_list(request): 
    worklogs = worklog.objects.all()  
    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    tickettype = ticket_type.objects.all()

    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year')
    user_id = request.GET.get('user_id')  
    billable_status = request.GET.get('billable_status')

    filters = {}

    # date filter
    if year or month:  
        try:
            if year:
                filters["date__year"] = int(year)
            if month:
                filters["date__month"] = int(month)
        except ValueError:
            pass  

    # user filter
    selected_user = None
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        filters["user"] = selected_user

    # billable filter
    if billable_status in ["0", "1"]:  
        is_billable = billable_status == "0"
        filters["billable"] = is_billable

    worklogs = worklogs.filter(**filters)

    
    existing_years = worklog.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    months = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    context = {
        'years': sorted(existing_years, reverse=True),
        'months': months,
        'year': int(year) if year else '',
        'month': int(month) if month else '',
        'worklogs': worklogs,
        'priority': priority,
        'tickets': tickets,
        'users': users,
        'tickettype': tickettype,
        'selected_user': selected_user,
        'billable_status': billable_status
    }

    return render(request, 'worklog.html', context)


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



