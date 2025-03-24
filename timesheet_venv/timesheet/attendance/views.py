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

#Attendance Details
@login_required
def attendance_view(request):
    if request.user.is_staff:
        users = User.objects.exclude(username=request.user.username)  
    else:
        users = User.objects.filter(username=request.user.username)  # Only show the current user for non-admins
    
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
    if not request.user.is_staff:
        attendance_records = attendance_records.filter(attendance__user=request.user)
    elif selected_user:  
        attendance_records = attendance_records.filter(attendance__user_id=selected_user)

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
        users = User.objects.exclude(username=request.user.username)  # Exclude the current admin user
    else:
        users = User.objects.filter(username=request.user.username)  # Only show the current user for non-admins
    return render(request, 'leavedetails.html', {
        'users': users,
                  })