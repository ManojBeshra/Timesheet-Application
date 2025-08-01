from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import worklog, requestreview, status
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
# import pandas as pd
from django.http import HttpResponse
# from openpyxl import Workbook
from django.utils.timezone import make_naive  # Import this
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils.dateparse import parse_date
from worklog.models import MailNotification

from user.utils import get_visible_users
@login_required
def worklog_list(request):
    visible_users = get_visible_users(request.user)
    worklogs = worklog.objects.filter(user__in=visible_users).order_by('-date')  # restrict to visible users
    priority = priority_type.objects.all()
    # users = visible_users  # only show users the current user can filter by
    users = User.objects.all()
    tickettype = ticket_type.objects.all()
    if request.user.is_staff:
        tickets = ticket.objects.all()
    else:
        user = request.user
        tickets = ticket.objects.filter(assigned_to=user)
        



    # Get filter parameters
    user_id = request.GET.get('user_id')  
    billable_status = request.GET.get('billable_status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')


    filters = {}


    # user filter
    selected_user = None
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        if selected_user in visible_users:
            filters["user"] = selected_user
        else:
            worklogs = worklog.objects.none()  # prevent unauthorized filtering
            selected_user = None  # reset since it's not valid


    # billable filter
    if billable_status in ["0", "1"]:
        is_billable = billable_status == "0"
        filters["billable"] = is_billable


    # Apply date filters
    if start_date:
        parsed_start_date = parse_date(start_date)
        if parsed_start_date:
            filters["date__gte"] = parsed_start_date  


    if end_date:
        parsed_end_date = parse_date(end_date)
        if parsed_end_date:
            filters["date__lte"] = parsed_end_date  


    # Apply filters
    worklogs = worklogs.filter(**filters)


    # Get unique dates for dropdowns
    unique_dates = worklog.objects.values_list('date', flat=True).distinct().order_by('date')

    statuses = status.objects.all()

    context = {
        'worklogs': worklogs,
        'priority': priority,
        'tickets': tickets,
        'users': users,
        'tickettype': tickettype,
        'selected_user': selected_user,
        'billable_status': billable_status,
        'start_date': start_date,
        'end_date': end_date,
        'unique_dates': unique_dates,
        'statuses': statuses
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


        if request.method == 'POST':
            if 'change_statusUser' in request.POST:
                try:
                    new_status = status.objects.get(status="Pending Review")
                    worklog_instance.status = new_status
                    worklog_instance.save()
                    messages.success(request, "Status changed to 'Pending Review'.")
                except status.DoesNotExist:
                    messages.error(request, "Status 'Pending Review' does not exist.")
                return redirect('worklog')
       
        if request.method == 'POST':
            if 'change_statusStaff' in request.POST:
                try:
                    new_status = status.objects.get(status="Reviewed")
                    worklog_instance.status = new_status
                    worklog_instance.save()
                    messages.success(request, "Status changed to 'Review'.")
                except status.DoesNotExist:
                    messages.error(request, "Status 'Pending Review' does not exist.")
                return redirect('worklog')
               
        if request.method == 'POST':
            if 'change_statusStaff2' in request.POST:
                try:
                    new_status = status.objects.get(status="Pending Review")
                    worklog_instance.status = new_status
                    worklog_instance.save()
                    messages.success(request, "Status changed to 'Pending Review'.")
                except status.DoesNotExist:
                    messages.error(request, "Status 'Pending Review' does not exist.")
                return redirect('worklog')


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
    statuses = status.objects.all()


    return render(request, 'worklogdetails.html', {
        'worklog': worklog_instance,
        'priority': priority,
        'tickets': tickets,
        'users': users,
        'tickettype': tickettype,
        'projects': projects,
        'statuses': statuses
    })


@csrf_exempt
@login_required
def add_worklog(request):
    if request.method == 'POST':
        data = json.loads(request.body)


        # Convert date string to datetime
        date_str = data.get("date")
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d")  # Convert to datetime


            # Inline week calculation
            first_day_of_month = date.replace(day=1)
            first_weekday = first_day_of_month.weekday()
            week_number = ((date.day + first_weekday) // 7) + 1
            week_string = f"Week {week_number}"
        else:
            return JsonResponse({"message": "Date is required!", "status": "error"}, status=400)






        # Create a new worklog entry
        worklog_instance = worklog.objects.create(
            user=request.user,  
            workdone=data.get("workdone"),
            hours=data.get("hours"),
            ticket_id=data.get("ticket"),
            date=date,
            week=week_string,
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


            # Get sender email (Logged-in user)
            sender_email = request.user.email if request.user.email else settings.EMAIL_HOST_USER
            print("Sender Email:", sender_email)


            # Fetch Admin Emails
            admin_users = User.objects.filter(is_superuser=True, email__isnull=False).values_list('email', flat=True)
            admin_emails = list(admin_users)
            print("Admin Emails:", admin_emails)


            if recipients:
                try:
                    send_mail(
                        subject="Worklog Review Request",
                        # message=f"{request_review.requested_note}\n\nwebsite url: http://127.0.0.1:5000/worklog/worklog/",
                        message = f"{request_review.requested_note}\n\nWebsite URL: {request.build_absolute_uri('/')[:-1]}",
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

import csv
@login_required
def export_worklogs_csv(request):
    # Get filter parameters
    user_id = request.GET.get('user_id')  
    billable_status = request.GET.get('billable_status')
    start_date = request.GET.get('start_date')  # New
    end_date = request.GET.get('end_date')  # New


    filters = {}


    # Apply filters
    if user_id:
        filters["user_id"] = int(user_id)
    if billable_status in ["0", "1"]:  
        filters["billable"] = billable_status == "0"


    # start_date filter
    if start_date:
        parsed_start_date = parse_date(start_date)
        if parsed_start_date:
            filters["date__gte"] = parsed_start_date  # Ensure it’s on or after the start date


    # end_date filter
    if end_date:
        parsed_end_date = parse_date(end_date)
        if parsed_end_date:
            filters["date__lte"] = parsed_end_date  # Ensure it’s on or before the end date


    # Fetch filtered worklogs
    worklogs = worklog.objects.filter(**filters).values(
        'user__username',
        'date',
        'ticket__ticket_id',  
        'ticket__ticket_title',  
        'billable',
        'workdone',  
        'hours',
        'ticket__ticket_type__name',
        'category'
    )


    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Worklogs.csv'


    writer = csv.writer(response)


    # Write header row
    writer.writerow([
        'User', 'Date', 'Ticket ID', 'Ticket Title',
        'Billable', 'Work Done', 'Hours', 'Project/Support', 'Category'
    ])


    # Write data rows
    for log in worklogs:
        date = log['date']
        if date:
            date = make_naive(date).strftime('%m/%d/%Y')  # Convert to MM/DD/YYYY


        billable = 'Billable' if log['billable'] else 'Non-Billable'


        writer.writerow([
            log['user__username'], date, log['ticket__ticket_id'], log['ticket__ticket_title'], billable, log['workdone'],
            log['hours'], log['ticket__ticket_type__name'], log['category']
        ])


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


#new fn

def dashboard_view(request):
    recent_notifications = MailNotification.objects.filter(user=request.user).order_by('-created_at')[:5]

    unseen_notification_count = MailNotification.objects.filter(user=request.user, notification_seen=False).count()

    context = {
        'recent_notifications': recent_notifications,
        'unseen_notification_count': unseen_notification_count,
    }

    return render(request, 'base.html', context)

def worklog_view(request):
    if request.user.is_authenticated:
        # Mark all unseen notifications as seen
        MailNotification.objects.filter(user=request.user, notification_seen=False).update(notification_seen=True)
#added
@login_required
def mark_notifications_seen(request):
    MailNotification.objects.filter(user=request.user, notification_seen=False).update(notification_seen=True)
    return JsonResponse({'status': 'ok'})
    print("Notifications seen marked for:", request.user)
