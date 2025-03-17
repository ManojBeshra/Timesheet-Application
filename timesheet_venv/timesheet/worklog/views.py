from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import worklog
from task . models import ticket, priority_type, ticket_type, project
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
import pandas as pd
from django.http import HttpResponse
from openpyxl import Workbook
from django.utils.timezone import make_naive  # Import this
from django.db.models.functions import ExtractYear, ExtractMonth

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

    
    # existing_years = worklog.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    months = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    context = {
        # 'years': sorted(existing_years, reverse=True),
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
def worklog_details(request, worklog_id):
    worklog_instance = get_object_or_404(worklog, id=worklog_id)
    if request.method == 'POST':
        
        form = worklog(request.POST)

        # Handle the billable field manually if not part of the form
        billable = request.POST.get('billable') == 'on'  # Check if the checkbox was checked
        form2 = WorklogForm(request.POST, instance=worklog_instance)
        
        current_user = User.objects.get(id = worklog_instance.user.id)

        # print(worklog_instance.user.username)
        if form2.is_valid():
            worklog_instance = form2.save(commit=False)
            worklog_instance.user = request.user
            worklog_instance.billable = billable  # Set the billable field from the form
            worklog_instance.save()
            worklog.objects.filter(id = worklog_instance.id).update(user=current_user)
            
            return redirect('worklog')
    else:
        form2 = WorklogForm(instance=worklog_instance)

    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    tickettype = ticket_type.objects.all()
    projects = project.objects.all()

    return render(request, 'worklogdetails.html', {
        'worklog': worklog_instance,
        'priority': priority,
        'tickets': tickets,
        'users': users,
        'tickettype': tickettype,
        'projects': projects,
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
            # week=data.get("week"),
            # priority_id=data.get("priority"),
            # project_support_id=data.get("project_support"),
            category=data.get("category"),
            # note=data.get("note"),
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

@login_required
def export_worklogs_excel(request):
    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year')
    user_id = request.GET.get('user_id')  
    billable_status = request.GET.get('billable_status')

    filters = {}

    # Apply filters
    if year:
        filters["date__year"] = int(year)
    if month:
        filters["date__month"] = int(month)
    if user_id:
        filters["user_id"] = int(user_id)
    if billable_status in ["0", "1"]:  
        filters["billable"] = billable_status == "0"

    # Fetch filtered worklogs
    worklogs = worklog.objects.filter(**filters).values(
        'user__username', 
        'date', 
        'ticket__ticket_id',  
        'ticket__ticket_title',  
        'priority__priority_name',  
        'billable',
        'workdone',  
        'hours',
        'project_support__name',
        'category'
    )

    # Convert to DataFrame
    df = pd.DataFrame(list(worklogs))

    # Convert timezone-aware DateTime to naive
    if 'date' in df.columns:
        df['date'] = df['date'].apply(lambda dt: make_naive(dt) if pd.notnull(dt) else dt)
        
        # Format date to MM/DD/YYYY
        df['date'] = df['date'].dt.strftime('%m/%d/%Y')

    # Rename columns
    df.rename(columns={
        'user__username': 'User',
        'date': 'Date',
        'ticket__ticket_id': 'Ticket ID',
        'ticket__ticket_title': 'Ticket Title',
        'priority__priority_name': 'Priority',
        'billable': 'Billable',
        'workdone': 'Work Done',
        'hours': 'Hours',
        'project_support__name': 'Porject/Support',
        'category': 'Category'
    }, inplace=True)

    # Map Billable field to readable values
    df['Billable'] = df['Billable'].map({True: 'Billable', False: 'Non-Billable'})
    
    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Worklogs.xlsx'
    
    # Write DataFrame to an Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Worklogs")

    return response

@csrf_exempt 
@login_required
def delete_worklog(request):
    if request.method == "POST":
        log_id = request.POST.get("id")
        worklogs = get_object_or_404(worklog, id=log_id)
        worklogs.delete()
        return JsonResponse({"success": True, "message": "Work log deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

