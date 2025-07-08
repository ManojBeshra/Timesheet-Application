from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from worklog.models import worklog
from task.models import ticket, state
from user.models import ManagerAssignment
import json
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
from attendance.models import Attendance, LeaveDetails, AttendanceDetail
from django.http import JsonResponse, HttpResponse
import csv
import io
from calendar import monthrange
from collections import defaultdict
import base64
from .models import AttendanceReport
from django.db.models.functions import ExtractYear


# function for calculating working days (weekdays)
def calculate_working_days(start_date, end_date):
    return sum(
        1 for d in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))
        if d.weekday() < 5  # Monday to Friday are considered
    )

# Function to calculate total leave days within a given range
def calculate_leave_taken(leave_qs, start_date, end_date):
    total_leave_days = 0
    for leave in leave_qs:
        leave_start = max(leave.leave_from, start_date)
        leave_end = min(leave.leave_to, end_date)
        if leave_start <= leave_end:
            # Count only Mon–Fri (working days)
            total_leave_days += sum(
                1 for d in (leave_start + timedelta(n) for n in range((leave_end - leave_start).days + 1))
                if d.weekday() < 5
            )
    return total_leave_days


#  for filtering attendance and leave data based on user, date range
def get_filtered_data(request, username=None, start_date=None, end_date=None):
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()

    if request.user.is_staff:
        if isinstance(username, User):
            selected_user = username
        elif username:
            selected_user = User.objects.filter(username=username).first()
        else:
            selected_user = None
        users = User.objects.all()
    else:
        selected_user = request.user
        users = None

    # If no user selected, return empty
    if not selected_user:
        return None, users, 0, 0, Attendance.objects.none(), []

    # Query leave details overlapping date range
    leave_qs = LeaveDetails.objects.filter(
        user=selected_user,
        leave_from__lte=end_date,
        leave_to__gte=start_date
    )

    total_working_days = calculate_working_days(start_date, end_date)
    leave_taken = calculate_leave_taken(leave_qs, start_date, end_date)

    attendance_data = Attendance.objects.filter(
        user=selected_user,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Compose PTO list for display
    pto_list = [{
        'pto': leave.type.name if leave.type else "N/A",
        'approved_by': leave.approval.name if leave.approval else "N/A",
        'total_days': leave_taken,
    } for leave in leave_qs]

    return selected_user, users, total_working_days, leave_taken, attendance_data, pto_list


# Get working weekdays in a given range
def get_weekdays(start_date, end_date):
    weekdays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday : 0–4
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    return weekdays

@login_required
def attendancereport_view(request):
    user_id = request.GET.get("user_id")
    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")

    try:
        year = int(selected_year)
    except (TypeError, ValueError):
        year = date.today().year

    try:
        month = datetime.strptime(selected_month, "%B").month if selected_month else None
    except ValueError:
        month = None

    #  date range for the month
    if month:
        start_date = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = date(year, month, end_day)
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    #  selected user
    selected_user = (
        User.objects.filter(id=user_id).first()
        if request.user.is_staff and user_id
        else request.user
    )

    if not selected_user:
        return render(request, "attendancereport.html", {"message": "User not found."})

    # Weekdays in selected date range (Mon-Fri only)
    weekdays = get_weekdays(start_date, end_date)
    total_working_days = len(weekdays)

    # Get present days (dates with Attendance records)
    attendance_records = Attendance.objects.filter(
    user=selected_user,
    date__range=(start_date, end_date)
)

    present_days = set(attendance_records)  # Set of Attendance objects

    # Query leave queryset 
    leave_qs = LeaveDetails.objects.filter(
        user=selected_user,
        leave_from__lte=end_date,
        leave_to__gte=start_date
    )
    pto_summary = defaultdict(lambda: {'total_days': 0, 'approved_by': set()})

    for leave in leave_qs:
        if not leave.type:
            continue
        days = (leave.leave_to - leave.leave_from).days + 1 if leave.leave_from and leave.leave_to else 0
        pto_name = leave.type.name
        pto_summary[pto_name]['total_days'] += days
        if leave.approval and leave.approval.name:
            pto_summary[pto_name]['approved_by'].add(leave.approval.name)

    pto_list = [
        {
            'pto': pto,
            'total_days': data['total_days'],
            'approved_by': ", ".join(data['approved_by']) if data['approved_by'] else "N/A"
        }
        for pto, data in pto_summary.items()
    ]

    leave_taken = calculate_leave_taken(leave_qs, start_date, end_date)
    working_days = total_working_days - leave_taken

    chart_labels = ['Leave Taken', 'Working Days']
    chart_data = [leave_taken, working_days]

    years_qs = Attendance.objects.dates('date', 'year')
    years = sorted(year.year for year in years_qs)
    months = [date(2000, m, 1).strftime('%B') for m in range(1, 13)]
    users = User.objects.all() if request.user.is_staff else None

    context = {
        "selected_user": selected_user,
        "leave_taken": leave_taken,         
        "total_working_days": total_working_days,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "attendance_records": attendance_records,  
        "years": years,
        "months": months,
        "users": users,
        "today": date.today(),
        # "pie_chart": pie_chart,
        "pto_list": pto_list,

    }

    return render(request, "attendancereport.html", context)

def logreport_view(request):
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project_id')

    # Base queryset for tickets
    tickets_qs = ticket.objects.all()
    filters_applied = False

    if user_id:
        tickets_qs = tickets_qs.filter(assigned_to__id=user_id)
        filters_applied = True
    if start_date:
        tickets_qs = tickets_qs.filter(date_opened__gte=parse_date(start_date))
        filters_applied = True
    if end_date:
        tickets_qs = tickets_qs.filter(closed_date__lte=parse_date(end_date))
        filters_applied = True
    if project_id:
        tickets_qs = tickets_qs.filter(project_support_id=project_id)
        filters_applied = True

    filtered_logs = worklog.objects.all()
    current_user = request.user

    # Apply user filter based on worklog.user
    # if user_id:
    #     filtered_logs = filtered_logs.filter(user_id=user_id)

    # Apply user-based filtering
    if not current_user.is_superuser:  # Normal user
        filtered_logs = filtered_logs.filter(user=current_user)
    elif user_id:  # Admin filtering by user from dropdown
        filtered_logs = filtered_logs.filter(user_id=user_id)

    # Apply date range filter (on worklog.date)
    if start_date:
        filtered_logs = filtered_logs.filter(date__gte=parse_date(start_date))
    if end_date:
        filtered_logs = filtered_logs.filter(date__lte=parse_date(end_date))

    # Billable and Non-Billable Hours Calculation
    billable_hours = filtered_logs.filter(billable=True).aggregate(total=Sum('hours'))['total'] or 0
    non_billable_hours = filtered_logs.filter(billable=False).aggregate(total=Sum('hours'))['total'] or 0
    total_hours = billable_hours + non_billable_hours


    # Apply user filter
    if not request.user.is_superuser:
        tickets_qs = tickets_qs.filter(assigned_to=request.user)
    elif user_id:
        tickets_qs = tickets_qs.filter(assigned_to__id=user_id)

    # Finalize ticket queryset
    tickets_qs = tickets_qs.distinct()

    # === Bar Chart: Ticket Types ===
    ticket_type_data = tickets_qs.values('ticket_type__name') \
        .annotate(ticket_count=Count('id')).order_by('ticket_type__name')

    ticket_types = [entry['ticket_type__name'] or "Unknown" for entry in ticket_type_data]
    ticket_counts = [entry['ticket_count'] for entry in ticket_type_data]

    # === Pie Chart / Summary Boxes: Ticket States ===
    state_counts_raw = tickets_qs.values('state__state_name') \
        .annotate(count=Count('id'))

    state_counts = {}
    for item in state_counts_raw:
        state_name = item['state__state_name'] or 'Unknown'
        key = state_name.strip().replace(' ', '_')
        state_counts[key] = item['count']

    # Add 0 for any missing known states (optional)
    all_states = state.objects.values_list('state_name', flat=True)
    for s in all_states:
        key = s.strip().replace(' ', '_')
        state_counts.setdefault(key, 0)



    # Apply filters to tickets for table
    tickets_qs_table = ticket.objects.all()

    if start_date:
        tickets_qs_table = tickets_qs_table.filter(date_opened__gte=parse_date(start_date))
    if end_date:
        tickets_qs_table = tickets_qs_table.filter(closed_date__lte=parse_date(end_date))
    if project_id:
        tickets_qs_table = tickets_qs_table.filter(project_support_id=project_id)

    # Apply user-based filtering
    if not request.user.is_superuser:
        # Normal user: show only tickets assigned to them
        tickets_qs_table = tickets_qs_table.filter(assigned_to=request.user)
    elif user_id:
        # Admin: filter by selected user if provided
        tickets_qs_table = tickets_qs_table.filter(assigned_to__id=user_id)

    # Final queryset for table
    table_tickets = tickets_qs_table.distinct().order_by('-date_opened')

    context = {
        'billable': billable_hours,
        'non_billable': non_billable_hours,
        'total_hours': total_hours,
        'ticket_types': ticket_types,
        'ticket_counts': ticket_counts,
        'bar_labels': json.dumps(ticket_types),
        'bar_counts': json.dumps(ticket_counts),
        'users': User.objects.all(),
        # 'projects': ticket.objects.all(),
        'projects': ticket.objects.all(),
        'selected_user': User.objects.filter(id=user_id).first() if user_id else None,
        'start_date': start_date,
        'end_date': end_date,
        'selected_project': project_id,
        'state_counts': state_counts,
        'table_tickets':table_tickets,
    }

    return render(request, 'logreport.html', context)

@login_required
def download_report(request):
    user_id = request.GET.get("user_id")
    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")

    try:
        year = int(selected_year)
    except (TypeError, ValueError):
        year = date.today().year

    try:
        month = datetime.strptime(selected_month, "%B").month if selected_month else None
    except ValueError:
        month = None

    if month:
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    user = (
        User.objects.filter(id=user_id).first()
        if request.user.is_staff and user_id
        else request.user
    )

    if not user:
        return JsonResponse({"message": "User not found."}, status=404)

    # Calculate working days
    total_working_days = calculate_working_days(start_date, end_date)

    # Fetch leaves for the user in the selected time 
    leave_qs = LeaveDetails.objects.filter(
        user=user,
        leave_from__lte=end_date,
        leave_to__gte=start_date
    )

    # Define the official leave types
    leave_types = [
        "Casual Leave",
        "Study Leave",
        "Compensatory Off",
        "Public Holidays",
        "Sick leave"
    ]

    # Initialize leave counters
    leave_counts = {lt: 0 for lt in leave_types}

    for leave in leave_qs:
        leave_start = max(leave.leave_from, start_date)
        leave_end = min(leave.leave_to, end_date)
        leave_days = (leave_end - leave_start).days + 1

        if leave_days > 0:
            leave_type = leave.type.name.strip()
            if leave_type in leave_counts:
                leave_counts[leave_type] += leave_days

    # Prepare CSV response
    response = HttpResponse(content_type="text/csv")
    filename = f"attendance_report_{user.username}_{year}_{selected_month or 'all'}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # Write CSV headers
    header = ["Username", "Email", "Year", "Month"] + leave_types + ["Total Working Days"]
    writer.writerow(header)

    # Write user data row
    row = [
        user.username,
        user.email,
        year,
        selected_month or "All"
    ] + [leave_counts[lt] for lt in leave_types] + [total_working_days]

    writer.writerow(row)

    return response

@login_required
def projectdetailsreport(request, ticket_id):
    manager = ManagerAssignment.objects.all()
    print("managers", manager)
    ticket_obj = ticket.objects.get(pk=ticket_id)

    # Calculate period cover
    if ticket_obj.closed_date and ticket_obj.date_opened:
        period_cover = (ticket_obj.closed_date - ticket_obj.date_opened).days
    else:
        period_cover = "N/A"

    # Filters from query params
    user_id = request.GET.get("user_id")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    current_user = request.user

    # Filter logs by ticket_title
    # filtered_logs = worklog.objects.filter(ticket__ticket_title=ticket_obj.ticket_title)
    filtered_logs = worklog.objects.filter(ticket__ticket_id=ticket_obj.ticket_id)

    # Apply user/date filters
    if not current_user.is_superuser:
        filtered_logs = filtered_logs.filter(user=current_user)
    elif user_id:
        filtered_logs = filtered_logs.filter(user_id=user_id)

    if start_date:
        filtered_logs = filtered_logs.filter(date__gte=parse_date(start_date))
    if end_date:
        filtered_logs = filtered_logs.filter(date__lte=parse_date(end_date))

    # Sum hours
    billable_hours = filtered_logs.filter(billable=True).aggregate(total=Sum('hours'))['total'] or 0
    non_billable_hours = filtered_logs.filter(billable=False).aggregate(total=Sum('hours'))['total'] or 0
    total_hours = billable_hours + non_billable_hours

    return render(request, 'project_details_report.html', {
        'ticket': ticket_obj,
        'period_cover': period_cover,
        'billable': billable_hours,
        'non_billable': non_billable_hours,
        'total_hours': total_hours,
        'users': User.objects.all(),
        'selected_user': User.objects.filter(id=user_id).first() if user_id else None,
        'start_date': start_date,
        'end_date': end_date,
        'manager': manager,
    })





def download_pro_report(request):
    # Query the necessary data for the report
    projects = ticket.objects.all()

    # Set up the response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="log_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sn', 'Task ID', 'Assigned Group', 'Start Date', 'Complete Date'])

    # Write the project data rows
    for idx, project in enumerate(projects, 1):
        assigned_users = ', '.join([user.first_name for user in project.assigned_to.all()])
        writer.writerow([idx, project.ticket_id, assigned_users, project.date_opened, project.closed_date or 'NULL'])

    return response