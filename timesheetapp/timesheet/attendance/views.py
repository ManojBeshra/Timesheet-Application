from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance, AttendanceDetail, LeaveDetails, LeaveType, User, userLeaveDays, EarnedLeaveDay
from django.utils import timezone
import datetime
from django.contrib.auth.models import User

#for excel and pdf
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas

#for pdf
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

#testing
from datetime import datetime
from django.db.models.functions import ExtractYear
import datetime
from datetime import date, time, datetime as dt

#for note
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from user.utils import get_visible_users
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from .models import LeaveDetails, LeaveType, Approval
from datetime import timedelta
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponse
from datetime import datetime
from .models import LeaveDetails, userLeaveDays, LeaveType

from django.utils.safestring import mark_safe

# Email 
from django.conf import settings
from email.message import EmailMessage
from django.core.mail import send_mail


@login_required
def attendance_view(request):
    visible_users = get_visible_users(request.user)
    users = visible_users


    years = AttendanceDetail.objects.annotate(year=ExtractYear('attendance__date')).values_list('year', flat=True).distinct().order_by('year')
   
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


    # Get filter parameters from request
    selected_user_id = request.GET.get('user_id')  
    selected_user = None  # default


    if selected_user_id:
        try:
            selected_user = User.objects.get(id=selected_user_id)  
        except User.DoesNotExist:
            selected_user = None  


    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
   
    # Initialize attendance records
    attendance_records = AttendanceDetail.objects.all().order_by('-attendance__date', '-entry')


    # Apply filters
    if request.user.profile.role == 'user':
        attendance_records = attendance_records.filter(attendance__user=request.user)
    elif selected_user and selected_user in visible_users:
        attendance_records = attendance_records.filter(attendance__user=selected_user)
    else:
        attendance_records = attendance_records.filter(attendance__user__in=visible_users)


    if selected_year:
        attendance_records = attendance_records.filter(attendance__date__year=int(selected_year))


    if selected_month:
        try:
            month_number = months.index(selected_month) + 1
            attendance_records = attendance_records.filter(attendance__date__month=month_number)
        except ValueError:
            pass


    data = [
        {
            'id': record.id,  
            'user': record.attendance.user.first_name,
            'date': record.attendance.date.strftime('%m/%d/%Y'),
            'entry': record.entry.strftime('%I:%M %p') if record.entry else 'N/A',
            'exit': record.exit.strftime('%I:%M %p') if record.exit else 'N/A',
            'hour': f"{record.hour // 3600} hr {(record.hour % 3600) // 60} min {record.hour % 60} sec" if record.hour else 'N/A',
            'note': record.note,
        }
        for record in attendance_records
    ]


    # Handle the form submission for adding a note
    if request.method == 'POST':
        note = request.POST.get('note')
        record_id = request.POST.get('record_id')  # Get the record ID from the form


        if note:
            if record_id:  # Check if record_id is not empty
                try:
                    record_id = int(record_id)  # Convert to integer
                    attendance_record = get_object_or_404(AttendanceDetail, id=record_id)
                    attendance_record.note = note  # Update the note
                    attendance_record.save()  # Save the changes
                    messages.success(request, "Note added successfully!")
                   
                    # Check if the request is an AJAX request
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'message': 'Note added successfully!'})
                except ValueError:
                    messages.error(request, "Invalid Record ID.")
            else:
                messages.error(request, "Record ID cannot be empty!")  # Handle empty record_id
        else:
            messages.error(request, "Note cannot be empty!")


        # Redirect to the attendance page for non-AJAX requests
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return redirect('attendance')  # Redirect to the attendance page


    # New: Handle selected record ID from GET request
    selected_record_id = request.GET.get('record_id')  # Assuming a `record_id` is passed via GET request
    selected_record = AttendanceDetail.objects.filter(id=selected_record_id).first()


    return render(request, 'attendance.html', {
        'users': users,
        'attendance_records': data,
        'years': years,
        'months': months,
        'selected_user': selected_user,  
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_record': selected_record,
       
    })

#Enrty/Exit Buttons
@login_required
def entry_view(request):
    if request.method == 'POST':
        user = request.user
        today_date = date.today()
        entry_time = dt.now().time()

        # Check if there is an existing entry without an exit
        existing_entry = AttendanceDetail.objects.filter(attendance__user=user, exit__isnull=True).exists()
        if existing_entry:
            return JsonResponse({'message': 'An entry already exists with no exit time recorded.'}, status=400)

        # Get or create attendance record for today
        attendance, created = Attendance.objects.get_or_create(user=user, date=today_date)
        AttendanceDetail.objects.create(attendance=attendance, entry=entry_time)

        # Fetch updated attendance records
        attendance_records = AttendanceDetail.objects.filter(attendance__user=user).order_by('-attendance__date', '-entry')
        data = [
            {
                # 'user': record.attendance.user.username,
                'user': record.attendance.user.first_name,
                # 'date': record.attendance.date.strftime('%B %d, %Y'),
                'date': record.attendance.date.strftime('%m/%d/%Y'),
                'entry': record.entry.strftime('%I:%M %p') if record.entry else 'N/A',
                'exit': record.exit.strftime('%I:%M %p') if record.exit else 'N/A',
                'hour': f"{record.hour // 3600} hr {(record.hour % 3600) // 60} min {record.hour % 60} sec" if record.hour else 'N/A',
                'note': record.note,

            }
            for record in attendance_records
        ]

        return JsonResponse({'message': 'Entry time recorded successfully.', 'data': data})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def exit_view(request):
    if request.method == 'POST':
        try:
            # Fetch the latest entry record for the user
            attendance_record = AttendanceDetail.objects.filter(attendance__user=request.user, exit__isnull=True).latest('entry')
            exit_time = dt.now().time()
            
            entry_time = dt.combine(attendance_record.attendance.date, attendance_record.entry)
            exit_time = dt.combine(attendance_record.attendance.date, exit_time)
            
            # Calculate duration in seconds
            duration = (exit_time - entry_time).total_seconds()
            attendance_record.exit = exit_time.time()
            attendance_record.hour = int(duration)
            attendance_record.save()

            # Fetch updated attendance records
            attendance_records = AttendanceDetail.objects.filter(attendance__user=request.user).order_by('-attendance__date', '-entry')
            data = [
                {
                    # 'user': record.attendance.user.username,
                    'user': record.attendance.user.first_name,
                    # 'date': record.attendance.date.strftime('%B %d, %Y'),
                    'date': record.attendance.date.strftime('%m/%d/%Y'),
                    'entry': record.entry.strftime('%I:%M %p') if record.entry else 'N/A',
                    'exit': record.exit.strftime('%I:%M %p') if record.exit else 'N/A',
                    'hour': f"{record.hour // 3600} hr {(record.hour % 3600) // 60} min {record.hour % 60} sec" if record.hour else 'N/A',
                    'note': record.note,
                }
                for record in attendance_records
            ]

            return JsonResponse({'message': 'Exit recorded successfully', 'data': data}, status=200)
        except AttendanceDetail.DoesNotExist:
            return JsonResponse({'message': 'No entry record found for today'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

#Note Button
def save_note_view(request, record_id):
    if request.method == "POST":
        note = request.POST.get("note", "").strip()
        if not note:
            return JsonResponse({"error": "Note cannot be empty!"}, status=400)

        # Fetch the record and update the note
        record = get_object_or_404(AttendanceDetail, id=record_id)
        record.note = note
        record.save()

        return JsonResponse({"message": "Note saved successfully!"})

    return JsonResponse({"error": "Invalid request method!"}, status=405)


#LEAVE
@login_required
def leavedetails_view(request):
    # User list for admin/ users
    if request.user.is_staff:
        users = User.objects.exclude(username=request.user.username)
    else:
        users = User.objects.filter(username=request.user.username)

    selected_user_id = request.GET.get('user_id')
    selected_date = request.GET.get('date')
    selected_category = request.GET.get('category')
    selected_status = request.GET.get('status')

    categories = LeaveType.objects.all()
    approvals = Approval.objects.all()

    leaves = LeaveDetails.objects.all()
    

    # if request.user.is_staff:
    #     unpaidcount = userLeaveDays.objects.filter(user_id=selected_user_id, type_id=5).first()
    # else:
    #     unpaidcount = userLeaveDays.objects.filter(user_id = request.user.id, type_id = 5).first()
    
    # if unpaidcount:
    #     unpaidcount = unpaidcount.leaveTaken
    # else:
    #     unpaidcount = 0

    # Filter leaves by user
    if request.user.is_staff and selected_user_id:
        leaves = leaves.filter(user__id=selected_user_id)
        user_for_leaves = User.objects.filter(id=selected_user_id).first()
    elif not request.user.is_staff:
        leaves = leaves.filter(user=request.user)
        user_for_leaves = request.user
    else:
        user_for_leaves = None

    #current year leave records
    current_year = datetime.now().year
    leaves = leaves.filter(requested_date__year=current_year)

    # Filter by date
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            leaves = leaves.filter(requested_date=date_obj)
        except ValueError:
            pass

    # Filter by category
    if selected_category:
        leaves = leaves.filter(type__name__iexact=selected_category)

    # Filter by status
    if selected_status:
        leaves = leaves.filter(approval__name__iexact=selected_status)

    # Selected user object
    selected_user = None
    if selected_user_id:
        try:
            selected_user = User.objects.get(id=selected_user_id)
        except User.DoesNotExist:
            selected_user = None

    # Get leave_from dates for JS validation (format as 'YYYY-MM-DD')
    # if user_for_leaves:
    #     existing_leave_from_dates = list(
    #         LeaveDetails.objects.filter(user=user_for_leaves).values_list('leave_from', flat=True)
    #     )
    #     existing_leave_from_dates = [d.strftime('%Y-%m-%d') for d in existing_leave_from_dates]
    # else:
    #     existing_leave_from_dates = []'

    # # Get leave_from dates for JS validation (format as 'YYYY-MM-DD')
    # leaves = LeaveDetails.objects.filter(user=request.user)

    existing_leaves = [
        {'leave_from': str(leave.leave_from), 'leave_to': str(leave.leave_to)}
        for leave in leaves
    ]



    # Calculate earned leave days from EarnedLeaveDay model
    earned_record = EarnedLeaveDay.objects.filter(user=user_for_leaves).first()
    earned_days = earned_record.earned_leave_days if earned_record else 0

    # Calculate total leave taken ONLY from approved leaves (exclude pending/denied)
    approved_statuses = ['Approved']  # Modify if needed
    leaves_approved = LeaveDetails.objects.filter(
        user=user_for_leaves,
        approval__name__in=approved_statuses
    )

    total_leave_taken = 0
    for leave in leaves_approved:
        total_leave_taken += weekdayscount(leave.leave_from, leave.leave_to)

    # Remaining leave days = earned - taken
    remaining_leave_days = earned_days - total_leave_taken
    if remaining_leave_days < 0:
        remaining_leave_days = 0  # Avoid negative

    unpaidcount = total_leave_taken-earned_days
    if unpaidcount < 0:
        unpaidcount = 0  # Avoid negative

    return render(request, 'leavedetails.html', {
        'users': users,
        'selected_user': selected_user,
        'leaves': leaves,
        'selected_category': selected_category,
        'selected_status': selected_status,
        'categories': categories,
        'approvals': approvals,
        'selected_date': selected_date,
        # 'existing_leaves': mark_safe(json.dumps(existing_leaves)),
        # 'existing_leave_from_dates': existing_leave_from_dates,
        'existing_leaves': existing_leaves,
        'total_leave_taken': total_leave_taken,
        'earned_days': earned_days,
        'remaining_leave_days': remaining_leave_days,
        'unpaidcount': unpaidcount,
    })


def weekdayscount(start_date, end_date):
    day_count = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() < 5:  # Monday=0 to Friday=4
            day_count += 1
        current_day += timedelta(days=1)
    return day_count



@login_required
def add_leave_details(request):
    if request.method != 'POST':
        return HttpResponse("Invalid method", status=405)

    leave_type_id = request.POST.get("type")
    leave_from = request.POST.get("leave_from")
    leave_to = request.POST.get("leave_to")
    description = request.POST.get("description", "")

    if not leave_type_id or not leave_from or not leave_to:
        return redirect(f"{reverse('leavedetails')}?error=Please fill all required fields.")

    try:
        leave_from_date = datetime.strptime(leave_from, '%Y-%m-%d').date()
        leave_to_date = datetime.strptime(leave_to, '%Y-%m-%d').date()
    except ValueError:
        return redirect(f"{reverse('leavedetails')}?error=Invalid date format.")

    days_requested = weekdayscount(leave_from_date, leave_to_date)
    if days_requested <= 0:
        return redirect(f"{reverse('leavedetails')}?error=No valid weekdays selected.")

    # Check duplicate leave_from date for the user
    if LeaveDetails.objects.filter(user=request.user, leave_from=leave_from_date).exists():
        return redirect(f"{reverse('leavedetails')}?error=Leave already taken for this start date.")

    # Get earned leave days based on tenure
    earned_record = EarnedLeaveDay.objects.filter(user=request.user).first()
    earned_days = earned_record.earned_leave_days if earned_record else 0

    # Calculate total leave taken (only approved leaves)
    approved_statuses = ['Approved']
    leaves_approved = LeaveDetails.objects.filter(
        user=request.user,
        approval__name__in=approved_statuses
    )

    total_leave_taken = 0
    for leave in leaves_approved:
        total_leave_taken += weekdayscount(leave.leave_from, leave.leave_to)

    remaining_days = earned_days - total_leave_taken

    # if remaining_days < days_requested:
    #     return redirect(f"{reverse('leavedetails')}?error=Insufficient remaining leave days.")

    approval = Approval.objects.get(name="Pending")


    leave = LeaveDetails.objects.create(
        user=request.user,
        type_id=leave_type_id,
        leave_from=leave_from_date,
        leave_to=leave_to_date,
        description=description,
        approval=approval,
    )

    leave.exceededdays = leave.exceeded_days or 0

    leave.save()


    send_leave_request_email(request.user, leave)

    return redirect(reverse('leavedetails'))



@csrf_exempt
@login_required
def approve_leave(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        leave_id = data.get('leave_id')
        approval_id = data.get('approval_id')
        remarks = data.get('remarks')
        description = data.get('description')

        try:
            leave = LeaveDetails.objects.get(id=leave_id)
            leave.approval_id = approval_id
            leave.approvedby = request.user
            leave.remarks = remarks
            leave.description = description
            leave.save()


            if leave.exceeded_days > 0:
                try:
                    unpaid_type = LeaveType.objects.get(name__iexact="Unpaid Leave")
                except LeaveType.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Unpaid Leave type not found'}, status=500)

                existing_unpaid = userLeaveDays.objects.filter(
                    user=leave.user,
                    type=unpaid_type  
                ).first()

                if existing_unpaid:
                    existing_unpaid.leaveTaken += leave.exceeded_days 
                    existing_unpaid.save()
                else:
                    userLeaveDays.objects.create(
                        user=leave.user,
                        type=unpaid_type,  
                        leaveTaken=leave.exceeded_days  
                    )

            
            return JsonResponse({'status': 'success'})
        except LeaveDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Leave not found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)



def send_leave_request_email(user, leave):
    try:
        leave_type_name = leave.type.name
    except:
        leave_type_name = "Unknown"
    
    exceeded_line = f"Unpaid Days: {leave.exceededdays} days \n" if leave.exceededdays else ""
    
    manager_email = User.objects.get(username = 'manager').email

    subject = f'Leave Request from {user.get_full_name()}'

    message = (
        f"Details of the Submitted Leave Request:\n\n"
        "----------------------------------------\n"
        f"Employee: {user.get_full_name()} ({user.email})\n"
        f"Leave Type: {leave_type_name}\n"
        f"From: {leave.leave_from}\n"
        f"To: {leave.leave_to}\n"
        f"Duration: {weekdayscount(leave.leave_from, leave.leave_to)} days \n"
        f"{exceeded_line}"
        f"Description: {leave.description}\n\n"
        "----------------------------------------\n\n"
        f"Please log in to the system to approve or reject this request."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email='noreply@glaciersystemsinc.com',
        recipient_list=[manager_email],
        fail_silently=False
    )




