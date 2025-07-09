from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance, AttendanceDetail 
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

#Leave Details
def leavedetails_view(request):
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

    leavedays = userLeaveDays.objects.filter(user = request.user)


    leaves = LeaveDetails.objects.all()

    # Filter by user
    if request.user.is_staff and selected_user_id:
        leaves = leaves.filter(user__id=selected_user_id)
    elif not request.user.is_staff:
        leaves = leaves.filter(user=request.user)

    # Filter by date
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            leaves = leaves.filter(requested_date=date_obj)
        except ValueError:
            pass  # ignore invalid dates

    # Filter by category
    if selected_category:
        leaves = leaves.filter(type__name__iexact=selected_category)

    # Filter by status
    if selected_status:
        leaves = leaves.filter(approval__name__iexact=selected_status)

    selected_user = None
    if selected_user_id:
        try:
            selected_user = User.objects.get(id=selected_user_id)
        except User.DoesNotExist:
            selected_user = None

    return render(request, 'leavedetails.html', {
        'users': users,
        'selected_user': selected_user,
        'leaves': leaves,  
        'selected_category': selected_category,
        'selected_status': selected_status,
        'categories': categories,
        'approvals': approvals,
        'selected_date': selected_date,
        'leavedays': leavedays
    })


# @login_required
# def add_leave_details(request):
#     if request.method == 'POST':
#         leave_type_id = request.POST.get("type")
#         leave_from = request.POST.get("leave_from")
#         leave_to = request.POST.get("leave_to")
#         approval_id = request.POST.get("approval")
#         description = request.POST.get("description")


#         if not leave_type_id or not leave_from or not leave_to:
#             return HttpResponse("Missing data", status=400)


#         LeaveDetails.objects.create(
#             user=request.user,
#             type_id=leave_type_id,
#             leave_from=leave_from,
#             leave_to=leave_to,
#             approval_id=approval_id,
#             description = description
#         )
#         return redirect('leavedetails')


#     return HttpResponse("Invalid method", status=405)

from datetime import timedelta

def weekdayscount(start_date, end_date):
    day_count = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() < 5:  
            day_count += 1
        current_day += timedelta(days=1)
    return day_count


from django.urls import reverse
from django.http import HttpResponse
from datetime import datetime
from .models import LeaveDetails, userLeaveDays, LeaveType

@login_required
def add_leave_details(request):
    if request.method == 'POST':
        leave_type_id = request.POST.get("type")
        leave_from = request.POST.get("leave_from")
        leave_to = request.POST.get("leave_to")
        approval_id = request.POST.get("approval")
        description = request.POST.get("description")

        # Calculate days requested
        leave_from_date = datetime.strptime(leave_from, '%Y-%m-%d').date()
        leave_to_date = datetime.strptime(leave_to, '%Y-%m-%d').date()
        days_requested = weekdayscount(leave_from_date, leave_to_date)
        if days_requested <= 0:
            return redirect(f"{reverse('leavedetails')}?error=No days selected.")


        # Update user leave days
        user_leave_days, created = userLeaveDays.objects.get_or_create(
            user=request.user,
            type_id=leave_type_id,
            defaults={'leaveTaken': 0, 'availableDays': LeaveType.objects.get(id=leave_type_id).days}
        )

        leave_type = LeaveType.objects.get(id=leave_type_id)

        if user_leave_days.availableDays < days_requested:  
            return redirect(
                f"{reverse('leavedetails')}?error=Not enough leave days. "
                f"You have only {user_leave_days.availableDays} days left for {leave_type.name}"
            )

        user_leave_days.leaveTaken += days_requested
        user_leave_days.save()

        # Create leave detail record
        LeaveDetails.objects.create(
            user=request.user,
            type_id=leave_type_id,
            leave_from=leave_from,
            leave_to=leave_to,
            approval_id=approval_id,
            description=description
        )

        return redirect(f"{reverse('leavedetails')}?msg=You have {user_leave_days.availableDays} days left of {user_leave_days.type.name} left")

    return HttpResponse("Invalid method", status=405)



@csrf_exempt
@login_required
def approve_leave(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        leave_id = data.get('leave_id')
        approval_id = data.get('approval_id')
        remarks = data.get('remarks')

        try:
            leave = LeaveDetails.objects.get(id=leave_id)
            leave.approval_id = approval_id
            leave.approvedby = request.user
            leave.remarks = remarks
            leave.save()
            
            return JsonResponse({'status': 'success'})
        except LeaveDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Leave not found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)

