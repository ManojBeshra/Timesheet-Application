import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), 'matplotlib_config')

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server

import matplotlib.pyplot as plt

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from worklog.models import worklog
from task.models import ticket, state
from user.models import ManagerAssignment, Teams
import json
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
from attendance.models import Attendance, LeaveDetails, AttendanceDetail, userLeaveDays
import csv
import io
from calendar import monthrange
from collections import defaultdict
import base64
from report.models import AttendanceReport
from django.db.models.functions import ExtractYear
import matplotlib.pyplot as plt
from io import StringIO
# import numpy as np
import re
# from .charts import createbargraphforteams, createbargraphbasedonteam  # Assuming location
from django.db.models import Q
from collections import defaultdict
from calendar import monthrange


# function to redirect report based on the users
@login_required
def report_redirect_view(request):
    if request.user.is_staff:
        return redirect('adminattendancereport')  
    else:
        return redirect('userattendancereport')  

# # old
# # function for calculating working days (weekdays)
# def calculate_working_days(start_date, end_date):
#     return sum(
#         1 for d in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))
#         if d.weekday() < 5  # Monday to Friday are considered
#     )


# # Function to calculate total leave days within a given range
# def calculate_leave_taken(leave_qs, start_date, end_date):
#     total_leave_days = 0
#     for leave in leave_qs:
#         leave_start = max(leave.leave_from, start_date)
#         leave_end = min(leave.leave_to, end_date)
#         if leave_start <= leave_end:
#             # Count only Mon–Fri (working days)
#             total_leave_days += sum(
#                 1 for d in (leave_start + timedelta(n) for n in range((leave_end - leave_start).days + 1))
#                 if d.weekday() < 5
#             )
#     return total_leave_days


# # for filtering attendance and leave data based on user, date range
# def get_filtered_data(request, username=None, start_date=None, end_date=None):
#     if not start_date:
#         start_date = date.today().replace(day=1)
#     if not end_date:
#         end_date = date.today()

#     if request.user.is_staff:
#         if isinstance(username, User):
#             selected_user = username
#         elif username:
#             selected_user = User.objects.filter(username=username).first()
#         else:
#             selected_user = None
#         users = User.objects.all()
#     else:
#         selected_user = request.user
#         users = None

#     # If no user selected, return empty
#     if not selected_user:
#         return None, users, 0, 0, Attendance.objects.none(), []

#     # Query leave details overlapping date range
#     leave_qs = LeaveDetails.objects.filter(
#         user=selected_user,
#         leave_from__lte=end_date,
#         leave_to__gte=start_date
#     )

#     total_working_days = calculate_working_days(start_date, end_date)
#     leave_taken = calculate_leave_taken(leave_qs, start_date, end_date)

#     attendance_data = Attendance.objects.filter(
#         user=selected_user,
#         date__range=[start_date, end_date]
#     ).order_by('date')

#     # Compose PTO list for display
#     pto_list = [{
#         'pto': leave.type.name if leave.type else "N/A",
#         'approved_by': leave.approval.name if leave.approval else "N/A",
#         'total_days': leave_taken,
#     } for leave in leave_qs]

#     return selected_user, users, total_working_days, leave_taken, attendance_data, pto_list


# # Get working weekdays in a given range
# def get_weekdays(start_date, end_date):
#     weekdays = []
#     current_date = start_date
#     while current_date <= end_date:
#         if current_date.weekday() < 5:  # Monday to Friday : 0–4
#             weekdays.append(current_date)
#         current_date += timedelta(days=1)
#     return weekdays


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


# @login_required
# def download_report(request):
#     user_id = request.GET.get("user_id")
#     selected_year = request.GET.get("year")
#     selected_month = request.GET.get("month")

#     try:
#         year = int(selected_year)
#     except (TypeError, ValueError):
#         year = date.today().year

#     try:
#         month = datetime.strptime(selected_month, "%B").month if selected_month else None
#     except ValueError:
#         month = None

#     if month:
#         start_date = date(year, month, 1)
#         end_date = date(year, month, monthrange(year, month)[1])
#     else:
#         start_date = date(year, 1, 1)
#         end_date = date(year, 12, 31)

#     user = (
#         User.objects.filter(id=user_id).first()
#         if request.user.is_staff and user_id
#         else request.user
#     )

#     if not user:
#         return JsonResponse({"message": "User not found."}, status=404)

#     # Calculate working days
#     total_working_days = calculate_working_days(start_date, end_date)

#     # Fetch leaves for the user in the selected time 
#     leave_qs = LeaveDetails.objects.filter(
#         user=user,
#         leave_from__lte=end_date,
#         leave_to__gte=start_date
#     )

#     # Define the official leave types
#     leave_types = [
#         "Casual Leave",
#         "Study Leave",
#         "Compensatory Off",
#         "Public Holidays",
#         "Sick leave"
#     ]

#     # Initialize leave counters
#     leave_counts = {lt: 0 for lt in leave_types}

#     for leave in leave_qs:
#         leave_start = max(leave.leave_from, start_date)
#         leave_end = min(leave.leave_to, end_date)
#         leave_days = (leave_end - leave_start).days + 1

#         if leave_days > 0:
#             leave_type = leave.type.name.strip()
#             if leave_type in leave_counts:
#                 leave_counts[leave_type] += leave_days

#     # Prepare CSV response
#     response = HttpResponse(content_type="text/csv")
#     filename = f"attendance_report_{user.username}_{year}_{selected_month or 'all'}.csv"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'

#     writer = csv.writer(response)

#     # Write CSV headers
#     header = ["Username", "Email", "Year", "Month"] + leave_types + ["Total Working Days"]
#     writer.writerow(header)

#     # Write user data row
#     row = [
#         user.username,
#         user.email,
#         year,
#         selected_month or "All"
#     ] + [leave_counts[lt] for lt in leave_types] + [total_working_days]

#     writer.writerow(row)

#     return response


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

# graph1
def createbargraphforteams(team_id=None, start_date=None, end_date=None):
    # Filter teams
    teams = Teams.objects.all()
    if team_id:
        teams = teams.filter(id=team_id)

    # Parse date range
    sd = parse_date(start_date) if start_date else None
    ed = parse_date(end_date) if end_date else None

    attendance_filter = {}
    if sd:
        attendance_filter['date__gte'] = sd
    if ed:
        attendance_filter['date__lte'] = ed

    attendance_qs = Attendance.objects.filter(**attendance_filter)

    approved_leaves = LeaveDetails.objects.filter(approval__name='Approved')
    if sd:
        approved_leaves = approved_leaves.filter(leave_from__lte=ed if ed else sd)
    if ed:
        approved_leaves = approved_leaves.filter(leave_to__gte=sd if sd else ed)

    x_labels = []
    worked_days = []
    leave_taken = []

    for team in teams:
        team_users = team.assigned_users.all()
        user_ids = team_users.values_list('id', flat=True)

        # Worked days: distinct dates per user
        attendance_days = (
            attendance_qs
            .filter(user__in=user_ids)
            .values('user_id', 'date')
            .distinct()
        )
        total_worked_days = attendance_days.count()

        # Leave days: from approved leave records
        team_leaves = approved_leaves.filter(user__in=user_ids)
        total_leave_days = 0
        for leave in team_leaves:
            if leave.leave_from and leave.leave_to:
                # Restrict leave to within selected date range
                lf = max(sd, leave.leave_from) if sd else leave.leave_from
                lt = min(ed, leave.leave_to) if ed else leave.leave_to
                if lf <= lt:
                    total_leave_days += (lt - lf).days + 1

        x_labels.append(team.teamname)
        worked_days.append(total_worked_days)
        leave_taken.append(total_leave_days)

    # num_bars = len(x_labels)
    # bar_width = 0.25 if num_bars == 1 else 0.2  # Make bar thinner if only one

    # fig, ax = plt.subplots(figsize=(4.5, 1.8))  # Keep figure width the same
    # x_pos = range(len(x_labels))
    # bars1 = ax.bar(x_pos, worked_days, width=bar_width, label="Worked Days", color="#9e6de0")
    # bars2 = ax.bar(x_pos, leave_taken, width=bar_width, bottom=worked_days, label="Leave Days", color="#fe5461")

    # # Labels on bars
    # for i, (worked, leave) in enumerate(zip(worked_days, leave_taken)):
    #     ax.text(i, worked / 2, str(worked), ha='center', va='center', fontsize=3.5, color='white', fontweight='bold')
    #     ax.text(i, worked + (leave / 2), str(leave), ha='center', va='center', fontsize=3.5, color='white', fontweight='bold')

    # ax.set_xticks(x_pos)
    # ax.set_xticklabels(x_labels, rotation=30, fontsize=4)
    # ax.set_ylabel("Days", fontweight="bold", fontsize=5)
    # ax.set_xlabel("Teams", fontweight="bold", fontsize=5)
    # ax.tick_params(axis='y', labelsize=4)
    # ax.legend(fontsize=4)
    # fig.tight_layout()

    num_bars = len(x_labels)

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(4.5, 1.8))  # Don't reduce figure width as requested

    # Set x positions and bar width
    if num_bars == 1:
        x_pos = [0.5]  # Center the single bar
        bar_width = 0.1  # Narrow bar for single team
        ax.set_xlim(0, 1)  # Space on both sides
    else:
        x_pos = range(num_bars)
        bar_width = 0.2

    # Plot bars
    bars1 = ax.bar(x_pos, worked_days, width=bar_width, label="Worked Days", color="#9e6de0")
    bars2 = ax.bar(x_pos, leave_taken, width=bar_width, bottom=worked_days, label="Leave Days", color="#fe5461")

    # Label bars
    for i, (worked, leave) in enumerate(zip(worked_days, leave_taken)):
        ax.text(x_pos[i], worked / 2, str(worked), ha='center', va='center', fontsize=3.5, color='white', fontweight='bold')
        ax.text(x_pos[i], worked + (leave / 2), str(leave), ha='center', va='center', fontsize=3.5, color='white', fontweight='bold')

    # Set labels and ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=30, fontsize=4)
    ax.set_ylabel("Days", fontweight="bold", fontsize=5)
    ax.set_xlabel("Teams", fontweight="bold", fontsize=5)
    ax.tick_params(axis='y', labelsize=4)
    ax.legend(fontsize=4)

    fig.tight_layout()

    # Export to SVG
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    svg_data = imgdata.getvalue()
    svg_data = re.sub(r'<svg[^>]*', lambda m: re.sub(r'(width|height)="[^"]+"', '', m.group(0)), svg_data)
    svg_data = svg_data.replace('<svg ', '<svg width="100%" ')

    return svg_data


# graph2
def createbargraphbasedonteam(team_id, start_date=None, end_date=None):
    try:
        team = Teams.objects.get(id=team_id)
    except Teams.DoesNotExist:
        return "<p>No team selected or team not found</p>"

    users = team.assigned_users.all()
    user_ids = users.values_list('id', flat=True)

    # Parse dates
    sd = parse_date(start_date) if start_date else None
    ed = parse_date(end_date) if end_date else None

    # Filter Attendance
    attendance_filter = Q(user__in=user_ids)
    if sd:
        attendance_filter &= Q(date__gte=sd)
    if ed:
        attendance_filter &= Q(date__lte=ed)
    attendance_qs = Attendance.objects.filter(attendance_filter).values('user', 'date').distinct()

    # Filter Approved Leaves
    leave_filter = Q(user__in=user_ids, approval__name="Approved")
    if sd:
        leave_filter &= Q(leave_from__lte=ed) if ed else Q(leave_from__gte=sd)
    if ed:
        leave_filter &= Q(leave_to__gte=sd) if sd else Q(leave_to__lte=ed)
    leave_qs = LeaveDetails.objects.filter(leave_filter)

    x = []
    workeddays = []
    leavetaken = []
    total_worked = 0
    total_leave = 0

    for user in users:
        x.append(user.first_name)

        # Worked days
        user_attendance = attendance_qs.filter(user=user).count()

        # Leave days
        user_leaves = leave_qs.filter(user=user)
        leavecount = 0
        for leave in user_leaves:
            if leave.leave_from and leave.leave_to:
                # Ensure leave period overlaps with filter range
                leave_start = max(leave.leave_from, sd) if sd else leave.leave_from
                leave_end = min(leave.leave_to, ed) if ed else leave.leave_to
                if leave_start <= leave_end:
                    leavecount += (leave_end - leave_start).days + 1

        workeddays.append(user_attendance)
        leavetaken.append(leavecount)
        total_worked += user_attendance
        total_leave += leavecount

    # Plotting (same as before)
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    bar_width = 0.4
    axs[0].set_xlim(-0.5, len(x) - 0.5)

    axs[0].bar(x, workeddays, label="Worked Days", color="#9e6de0", width=bar_width)
    axs[0].bar(x, leavetaken, bottom=workeddays, label="Leave Days", color="#fe5461", width=bar_width)

    for i, (worked, leave) in enumerate(zip(workeddays, leavetaken)):
        axs[0].text(i, worked / 2, str(worked), ha='center', va='center', fontsize=7, color='white', fontweight='bold')
        axs[0].text(i, worked + (leave / 2), str(leave), ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    axs[0].set_ylabel("Days", fontweight="bold", fontsize=8)
    axs[0].set_xlabel("Users", fontweight="bold", fontsize=8)
    axs[0].set_title(f"Days per User - {team.teamname}", fontsize=10)
    axs[0].tick_params(axis='x', labelrotation=30, labelsize=7)
    axs[0].tick_params(axis='y', labelsize=7)
    axs[0].legend(fontsize=6)

    # axs[1].pie(
    #     [total_worked, total_leave],
    #     labels=["Worked", "Leave"],
    #     autopct='%1.1f%%',
    #     colors=["#9e6de0", "#fe5461"],
    #     textprops={'fontsize': 8, 'color': 'white'}
    # )
    # axs[1].set_title("Team Total Distribution", fontsize=10)

    # Pie Chart
    if total_worked + total_leave > 0:
        axs[1].pie(
            [total_worked, total_leave],
            labels=["Worked", "Leave"],
            autopct='%1.1f%%',
            colors=["#9e6de0", "#fe5461"],
            textprops={'fontsize': 8, 'color': 'white'}
        )
        axs[1].set_title("Team Total Distribution", fontsize=10)
    else:
        axs[1].text(0.5, 0.5, "No data", ha='center', va='center', fontsize=10, color='white')
        axs[1].set_title("No Data Available", fontsize=10)

    fig.tight_layout()

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    return imgdata.getvalue()


# admin report view
def adminattendancereport_view(request):
    team_id = request.GET.get('team_id')
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = datetime.today().date()
    existing_years = set(AttendanceReport.objects.values_list('year', flat=True))
    existing_years.add(today.year)
    filters_applied = any([team_id, selected_year, selected_month, start_date, end_date])

    reports = AttendanceReport.objects.all()
    selected_team = None
    team_users = User.objects.none()

    # --- Team Filter ---
    if team_id:
        selected_team = Teams.objects.filter(id=team_id).first()
        if selected_team:
            team_users = selected_team.assigned_users.all()
            reports = reports.filter(user__in=team_users)

    # --- Year Filter ---
    year = None
    if selected_year:
        try:
            year = int(selected_year)
            reports = reports.filter(year=year)
        except ValueError:
            pass

    # --- Month Filter ---
    selected_month_label = None
    if selected_month:
        try:
            month_num = int(selected_month)
            reports = reports.filter(month=month_num)
        except ValueError:
            selected_month_label = selected_month

    # --- Date Range Filter (Start/End Date) ---
    date_filtered_user_ids = None
    if start_date or end_date:
        sd = parse_date(start_date) if start_date else None
        ed = parse_date(end_date) if end_date else None

        detail_filter = {}
        if sd:
            detail_filter['attendance__date__gte'] = sd
        if ed:
            detail_filter['attendance__date__lte'] = ed

        attendance_details = AttendanceDetail.objects.filter(**detail_filter)
        date_filtered_user_ids = attendance_details.values_list('attendance__user_id', flat=True).distinct()

    if date_filtered_user_ids is not None:
        reports = reports.filter(user_id__in=date_filtered_user_ids)

    # --- Generate Graphs ---
    # graph1 = createbargraphforteams(reports) if request.user.is_staff else ""
    graph1 = createbargraphforteams(team_id, start_date, end_date) if request.user.is_staff else ""
    # graph2 = createbargraphbasedonteam(team_id) if selected_team else ""
    graph2 = createbargraphbasedonteam(team_id, start_date, end_date) if selected_team else ""


    context = {
        'reports': reports,
        'graph1': graph1,
        'graph2': graph2,
        'teams': Teams.objects.all(),
        'years': sorted(existing_years, reverse=True),
        'months': [label for _, label in AttendanceReport.MONTH_CHOICES],
        'selected_team': selected_team,
        'team_users': team_users,
        'selected_year': year,
        'selected_month': selected_month,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
        'filters_applied': filters_applied,
    }

    return render(request, 'adminattendancereport.html', context)


# # user report view
# @login_required
# def userattendancereport_view(request):
#     user_id = request.GET.get("user_id")
#     selected_year = request.GET.get("year")
#     selected_month = request.GET.get("month")

#     # Handle year selection or default to current
#     try:
#         year = int(selected_year)
#     except (TypeError, ValueError):
#         year = date.today().year

#     # Handle month selection or full year
#     try:
#         month = datetime.strptime(selected_month, "%B").month if selected_month else None
#     except ValueError:
#         month = None

#     if month:
#         start_date = date(year, month, 1)
#         end_date = date(year, month, monthrange(year, month)[1])
#     else:
#         start_date = date(year, 1, 1)
#         end_date = date(year, 12, 31)

#     # User context
#     selected_user = (
#         User.objects.filter(id=user_id).first()
#         if request.user.is_staff and user_id
#         else request.user
#     )

#     if not selected_user:
#         return render(request, "userattendancereport.html", {"message": "User not found."})

#     weekdays = get_weekdays(start_date, end_date)
#     total_working_days = len(weekdays)

#     # Attendance
#     attendance_records = Attendance.objects.filter(
#         user=selected_user,
#         date__range=(start_date, end_date)
#     )
#     present_days = set(attendance_records)

#     # Leave calculation
#     leave_qs = LeaveDetails.objects.filter(
#         user=selected_user,
#         leave_from__lte=end_date,
#         leave_to__gte=start_date
#     )

#     pto_summary = defaultdict(lambda: {'total_days': 0, 'approved_by': set()})
#     for leave in leave_qs:
#         if not leave.type:
#             continue
#         days = (leave.leave_to - leave.leave_from).days + 1 if leave.leave_from and leave.leave_to else 0
#         pto_summary[leave.type.name]['total_days'] += days
#         if leave.approval and leave.approval.name:
#             pto_summary[leave.type.name]['approved_by'].add(leave.approval.name)

#     pto_list = [
#         {
#             'pto': pto,
#             'total_days': data['total_days'],
#             'approved_by': ", ".join(data['approved_by']) if data['approved_by'] else "N/A"
#         }
#         for pto, data in pto_summary.items()
#     ]

#     leave_taken = calculate_leave_taken(leave_qs, start_date, end_date)
#     working_days = total_working_days - leave_taken

#     # Filters
#     years_qs = Attendance.objects.dates('date', 'year')
#     years = sorted(year.year for year in years_qs)
#     months = [date(2000, m, 1).strftime('%B') for m in range(1, 13)]
#     users = User.objects.all() if request.user.is_staff else None

#     context = {
#         "selected_user": selected_user,
#         "leave_taken": leave_taken,
#         "total_working_days": total_working_days,
#         "selected_year": selected_year,
#         "selected_month": selected_month,
#         "attendance_records": attendance_records,
#         "years": years,
#         "months": months,
#         "users": users,
#         "today": date.today(),
#         "pto_list": pto_list,
#     }

#     return render(request, "userattendancereport.html", context)


def calculate_leave_taken(leave_qs, start_date, end_date):
    total = 0
    for leave in leave_qs:
        leave_start = max(leave.leave_from, start_date)
        leave_end = min(leave.leave_to, end_date)
        days = (leave_end - leave_start).days + 1 if leave_start and leave_end else 0
        if leave.approval and leave.approval.name.lower() == 'approved':
            total += days
    return total

def get_weekdays(start_date, end_date):
    return [d for d in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)) if d.weekday() < 5]

def generate_user_attendance_pie(working_days, leave_taken):
    labels = ['Worked Days', 'Leave Days']
    sizes = [working_days, leave_taken]
    colors = ['#9e6de0', '#fe5461']

    # fig, ax = plt.subplots(figsize=(2.5, 2.5))
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    ax.axis('equal')
    fig.tight_layout()

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    svg_data = imgdata.getvalue()

    # Clean SVG (make it responsive)
    svg_data = re.sub(r'<svg[^>]*', lambda m: re.sub(r'(width|height)="[^"]+"', '', m.group(0)), svg_data)
    svg_data = svg_data.replace('<svg ', '<svg width="100%" ')
    return svg_data

@login_required
def userattendancereport_view(request):
    user_id = request.GET.get("user_id")
    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")
    start_date_param = request.GET.get("start_date")
    end_date_param = request.GET.get("end_date")

    # Default year/month
    try:
        year = int(selected_year)
    except (TypeError, ValueError):
        year = date.today().year

    try:
        month = datetime.strptime(selected_month, "%B").month if selected_month else None
    except ValueError:
        month = None

    # Default date range from year/month
    if month:
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    # Override with actual start/end date if given
    sd = parse_date(start_date_param) if start_date_param else None
    ed = parse_date(end_date_param) if end_date_param else None
    if sd:
        start_date = sd
    if ed:
        end_date = ed

    # Get user
    selected_user = (
        User.objects.filter(id=user_id).first()
        if request.user.is_staff and user_id
        else request.user
    )

    if not selected_user:
        return render(request, "userattendancereport.html", {"message": "User not found."})

    # Working days
    weekdays = get_weekdays(start_date, end_date)
    total_working_days = len(weekdays)

    # Attendance records
    attendance_records = Attendance.objects.filter(
        user=selected_user,
        date__range=(start_date, end_date)
    )

    # Leave details
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
        pto_summary[leave.type.name]['total_days'] += days
        if leave.approval and leave.approval.name:
            pto_summary[leave.type.name]['approved_by'].add(leave.approval.name)

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

    # Generate pie chart SVG
    pie_chart_svg = generate_user_attendance_pie(working_days, leave_taken)

    # Filters
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
        "pto_list": pto_list,
        "pie_chart_svg": pie_chart_svg,
        "selected_start_date": start_date,
        "selected_end_date": end_date,
    }

    return render(request, "userattendancereport.html", context)




# download admin attendance report
def downloadadminattendancereport_view(request):
    team_id = request.GET.get('team_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Parse dates
    sd = parse_date(start_date) if start_date else None
    ed = parse_date(end_date) if end_date else None

    # Filter attendance
    attendance_qs = Attendance.objects.all()
    leave_qs = LeaveDetails.objects.filter(approval__name='Approved')

    if sd:
        attendance_qs = attendance_qs.filter(date__gte=sd)
        leave_qs = leave_qs.filter(leave_from__lte=ed)  # leave_from can start earlier
    if ed:
        attendance_qs = attendance_qs.filter(date__lte=ed)
        leave_qs = leave_qs.filter(leave_to__gte=sd)  # leave_to can end later

    if team_id:
        team = Teams.objects.filter(id=team_id).first()
        if team:
            assigned_users = team.assigned_users.all()
            attendance_qs = attendance_qs.filter(user__in=assigned_users)
            leave_qs = leave_qs.filter(user__in=assigned_users)

    # Prepare team-wise summary
    team_summary = {}
    for team in Teams.objects.all():
        if team_id and str(team.id) != str(team_id):
            continue

        users = team.assigned_users.all()
        user_ids = users.values_list('id', flat=True)

        worked_days = attendance_qs.filter(user__in=user_ids).values('user', 'date').distinct().count()

        leave_days = 0
        team_leaves = leave_qs.filter(user__in=user_ids)
        for leave in team_leaves:
            if leave.leave_from and leave.leave_to:
                from_date = max(leave.leave_from, sd) if sd else leave.leave_from
                to_date = min(leave.leave_to, ed) if ed else leave.leave_to
                leave_days += (to_date - from_date).days + 1

        team_summary[team.teamname] = {
            'worked_days': worked_days,
            'leave_days': leave_days,
        }

    # Prepare user-wise summary
    user_summary = {}
    users = attendance_qs.values_list('user', flat=True).distinct()
    for user_id in users:
        user_attendance = attendance_qs.filter(user_id=user_id).values('date').distinct().count()

        user_leaves = leave_qs.filter(user_id=user_id)
        user_leave_days = 0
        for leave in user_leaves:
            if leave.leave_from and leave.leave_to:
                from_date = max(leave.leave_from, sd) if sd else leave.leave_from
                to_date = min(leave.leave_to, ed) if ed else leave.leave_to
                user_leave_days += (to_date - from_date).days + 1

        user_obj = Attendance.objects.filter(user_id=user_id).first().user
        user_summary[user_obj.get_full_name()] = {
            'worked_days': user_attendance,
            'leave_days': user_leave_days
        }

    # Build CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_attendance_report.csv"'

    writer = csv.writer(response)

    writer.writerow(['Team-Wise'])
    writer.writerow(['Team', 'Filter From', 'Filter To', 'Worked Days', 'Leave Days'])
    for teamname, data in team_summary.items():
        writer.writerow([
            teamname,
            start_date or '',
            end_date or '',
            data['worked_days'],
            data['leave_days']
        ])

    writer.writerow([])  # Blank line
    writer.writerow(['User-Wise'])
    writer.writerow(['Username', 'Filter From', 'Filter To', 'Worked Days', 'Leave Days'])
    for username, data in user_summary.items():
        writer.writerow([
            username,
            start_date or '',
            end_date or '',
            data['worked_days'],
            data['leave_days']
        ])

    return response
