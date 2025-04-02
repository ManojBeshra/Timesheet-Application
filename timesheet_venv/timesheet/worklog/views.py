from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import worklog, requestreview
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
import pandas as pd
from django.http import HttpResponse
from openpyxl import Workbook
from django.utils.timezone import make_naive  # Import this
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils.dateparse import parse_date



@login_required
def worklog_list(request): 
    worklogs = worklog.objects.all().order_by('-date')
    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    tickettype = ticket_type.objects.all()

    # Get filter parameters
    user_id = request.GET.get('user_id')  
    billable_status = request.GET.get('billable_status')
    start_date = request.GET.get('start_date')  # new parameter
    end_date = request.GET.get('end_date')  # new parameter

    filters = {}

    # If the logged-in user is not staff
    if not request.user.is_staff:
        worklogs = worklogs.filter(user=request.user)

    # user filter
    selected_user = None
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        filters["user"] = selected_user

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

    # Context to maintain filter values on page reload
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
        'unique_dates': unique_dates

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

# @login_required
# def requestreview_mail(request):
#     if request.method == "POST":
#         form = RequestreviewForm(request.POST)
#         if form.is_valid():
#             request_review = form.save(commit=False)
#             request_review.save()
#             form.save_m2m()  # Save ManyToMany field after saving instance
            
#             recipients = [user.email for user in request_review.send_to.all() if user.email]

#             if recipients:
#                 try:
#                     send_mail(
#                         subject="Worklog Review Request",
#                         message=f"{request_review.requested_note}\n\nwebsite url: http://127.0.0.1:5000/worklog/worklog/",
#                         from_email=settings.EMAIL_HOST_USER,
#                         recipient_list=recipients,
#                         fail_silently=False,
#                     )
#                     messages.success(request, "Email sent successfully!") 
#                 except Exception as e:
#                     messages.error(request, f"Error sending email: {e}")  

#             return redirect("worklog")  

#     else:
#         form = RequestreviewForm()

#     return render(request, "worklog.html", {"form": form})


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




# from email.message import EmailMessage
# @login_required
# def requestreview_mail(request):
#     if request.method == "POST":
#         form = RequestreviewForm(request.POST)
#         if form.is_valid():
#             request_review = form.save(commit=False)
#             request_review.save()
#             form.save_m2m()  # Save ManyToMany field after saving instance
           
#             recipients = [user.email for user in request_review.send_to.all() if user.email]


#             # Get sender email (Logged-in user or fallback)
#             sender_email = request.user.email if request.user.email else settings.EMAIL_HOST_USER
#             reply_to_email = sender_email  # Use the sender as the Reply-To address


#             # Generate dynamic base URL
#             base_url = request.build_absolute_uri('/')[:-1]
#             message = f"{request_review.requested_note}\n\n{base_url}"


#             # Create email with reply-to
#             email = EmailMessage(
#                 subject="Worklog Review Request",
#                 body=f"{request_review.requested_note}\n\n{base_url}",
#                 from_email=settings.EMAIL_HOST_USER,  # Ensure sender is set properly
#                 to=recipients,
#                 reply_to=[reply_to_email],  # Adding Reply-To header
#             )


#             # Send email
#             email.send(fail_silently=False)


#             return redirect("worklog")  


#     else:
#         form = RequestreviewForm()


#     return render(request, "worklog.html", {"form": form})





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

