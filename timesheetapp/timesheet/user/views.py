from django.shortcuts import render, get_object_or_404
from .models import Profile
from attendance.models import EarnedLeaveDay, LeaveDetails
from worklog.models import worklog
from datetime import timedelta
from task.models import ticket, project
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth

def weekdayscount(start_date, end_date):
    day_count = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() < 5:  # Monday=0 to Friday=4
            day_count += 1
        current_day += timedelta(days=1)
    return day_count


def useramount(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    billable_hours = 0
    earnleave = EarnedLeaveDay.objects.get(user=user)
    joined_date = earnleave.joined_date
    tickets = ticket.objects.filter(assigned_to=user, state =4)\
    

    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # Filter billable worklogs for current month only
    worklogs = worklog.objects.filter(
        user=user,
        billable=True,
        date__year=current_year,
        date__month=current_month
    )

    for i in worklogs:
        billable_hours += i.hours

    if profile.salaried == False:
        totalamount = billable_hours * profile.wages
    else:
        totalamount = 0

    # Calculate total leave taken ONLY from approved leaves (exclude pending/denied)
    approved_statuses = ['Approved']  # Modify if needed
    leaves_approved = LeaveDetails.objects.filter(
        user=user,
        approval__name__in=approved_statuses
    )

    total_leave_taken = 0
    for leave in leaves_approved:
        total_leave_taken += weekdayscount(leave.leave_from, leave.leave_to)

    issues = 0
    for j in tickets:
        issues += 1

    if not request.user.is_staff:
        projects = project.objects.filter(ticket__assigned_to=user).distinct()
    else:
        projects = project.objects.all()

    projectcount = 0
    for k in projects:
        projectcount +=1
        
    
    context = {
        'user': user,
        'profile': profile,
        'issues_resolved': issues,
        'billable_hours': billable_hours,
        'pto_taken': total_leave_taken,
        'totalamount': totalamount,
        'joined_date': joined_date,
        'projects_involved': projectcount
    }

    return render(request, 'useramount.html', context)

    