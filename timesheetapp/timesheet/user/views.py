from django.shortcuts import render, get_object_or_404
from user.models import Profile, Teams
from .models import User
from attendance.models import EarnedLeaveDay, LeaveDetails
from worklog.models import worklog
from task.models import ticket, project
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db.models.functions import TruncMonth
from calendar import monthrange


def weekdayscount(start_date, end_date):
    day_count = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() < 5:  # Monday=0 to Friday=4
            day_count += 1
        current_day += timedelta(days=1)
    return day_count


def userdetails(request):

    if request.user.is_staff and request.GET.get('user_id'):
        user = get_object_or_404(User, id=request.GET.get('user_id'))
    else:
        user = request.user

    # user = request.user
    profile = get_object_or_404(Profile, user=user)
    earnleave = EarnedLeaveDay.objects.get(user=user)
    joined_date = earnleave.joined_date
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month

    # Month start and end
    month_start = date(current_year, current_month, 1)
    last_day = monthrange(current_year, current_month)[1]
    month_end = date(current_year, current_month, last_day)

    # Earned leave till today (based on years worked)
    total_earned_leave = earnleave.calculate_earned_leave()

    # Approved leaves taken before this month
    approved_statuses = ['Approved']
    past_leaves = LeaveDetails.objects.filter(
        user=user,
        approval__name__in=approved_statuses,
        leave_to__lt=month_start
    )

    leave_taken_before_this_month = 0
    for leave in past_leaves:
        effective_start = max(leave.leave_from, joined_date)
        effective_end = leave.leave_to
        leave_taken_before_this_month += weekdayscount(effective_start, effective_end)

    remaining_earned_leave = total_earned_leave - leave_taken_before_this_month

    # Approved leaves during current month (partial overlaps considered)
    current_month_leaves = LeaveDetails.objects.filter(
        user=user,
        approval__name__in=approved_statuses,
        leave_to__gte=month_start,
        leave_from__lte=month_end
    )

    leave_taken_this_month = 0
    for leave in current_month_leaves:
        effective_start = max(leave.leave_from, month_start)
        effective_end = min(leave.leave_to, month_end)
        leave_taken_this_month += weekdayscount(effective_start, effective_end)

    # Final unpaid leave calculation
    unpaid_leave_days = max(leave_taken_this_month - remaining_earned_leave, 0)

    # Billable hours & amount (for hourly workers)
    billable_hours = 0
    totalamount = 0
    worklogs = worklog.objects.filter(
        user=user,
        billable=True,
        date__year=current_year,
        date__month=current_month
    )
    for i in worklogs:
        billable_hours += i.hours

    if not profile.salaried:
        totalamount = billable_hours * profile.wages

    # Salary adjustment for unpaid leave (salaried users)
    FIXED_WORKING_DAYS = 30
    if profile.salaried:
        per_day_salary = profile.wages / FIXED_WORKING_DAYS
        adjusted_salary = profile.wages - (unpaid_leave_days * per_day_salary)
    else:
        adjusted_salary = totalamount

    # Get worklogs for this user this month
    worklogs_this_month = worklog.objects.filter(
        user=user,
        date__date__range=(month_start, month_end)
    ).select_related('ticket')

    # Extract all ticket_ids worked on this month (excluding nulls)
    ticket_ids = worklogs_this_month.values_list('ticket__ticket_id', flat=True)

    # Filter ticket IDs that actually start with 'PRO' and collect distinct ones
    pro_ticket_ids = set(
        tid for tid in ticket_ids if tid and tid.startswith('PR')
    )

    projectcount = len(pro_ticket_ids)  # Number of distinct 'PRO' tickets

    # Count resolved tickets
    resolved_ticket_ids = worklog.objects.filter(
        user=user,
        date__date__range=(month_start, month_end),
        ticket__state__id=4
    ).values_list('ticket_id', flat=True).distinct()

    issues = ticket.objects.filter(id__in=resolved_ticket_ids).count()
    # print("issues:", issues)
    # print("PRO ticket IDs worked on:", pro_ticket_ids)
    # print("projectcount:", projectcount)
    # print("All ticket IDs this month:", list(ticket_ids))

    context = {
        'user': user,
        'profile': profile,
        'joined_date': joined_date,
        'issues_resolved': issues,
        'projects_involved': projectcount,
        'billable_hours': billable_hours,
        'pto_taken': leave_taken_this_month,
        'unpaid_leave_days': round(unpaid_leave_days, 2),
        'totalamount': totalamount,
        'adjusted_salary': round(adjusted_salary, 2),
    }

    return render(request, 'userdetails.html', context)


def teamdetail(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # Get selected_team_id from GET parameters, default to 1 if missing or invalid
    selected_team_id = request.GET.get('team_id')
    if selected_team_id in [None, '', '0']:
        selected_team_id = 1
    else:
        selected_team_id = int(selected_team_id)

    selected_team = None
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # Initialize empty querysets to avoid errors if no team or no data found
    worklogs = worklog.objects.none()
    leaves_approved = LeaveDetails.objects.none()
    tickets = ticket.objects.none()
    projects = project.objects.none()

    if selected_team_id:
        selected_team = Teams.objects.filter(id=selected_team_id).first()

        if selected_team:
            # Get all users in the selected team
            team_users = selected_team.assigned_users.all()
            usercount = team_users.count()
            # Filter worklogs for team users, billable, and in current month/year
            worklogs = worklog.objects.filter(
                user__in=team_users,
                billable=True,
                date__year=current_year,
                date__month=current_month
            )

            # Filter approved leaves for these users
            approved_statuses = ['Approved']
            leaves_approved = LeaveDetails.objects.filter(
                user__in=team_users,
                approval__name__in=approved_statuses
            )

            # Tickets assigned to any user in the team
            tickets = ticket.objects.filter(
                assigned_to__in=team_users
            ).distinct()

            # Projects associated with those tickets
            projects = project.objects.filter(
                ticket__assigned_to__in=team_users
            ).distinct()
        else:
            projects = project.objects.none()
    else:
        projects = project.objects.all()

    # Calculate total billable hours (handle possible None in hours)
    billable_hours = sum(w.hours or 0 for w in worklogs)
    print(f"Worklogs count: {worklogs.count()}")
    for w in worklogs:
        print(f"user={w.user}, hours={w.hours}, billable={w.billable}, date={w.date}")

    # Calculate total leave days taken from approved leaves
    total_leave_taken = sum(
        weekdayscount(leave.leave_from, leave.leave_to) for leave in leaves_approved
    )

    # Count of tickets assigned (issues resolved)
    issues = tickets.count()

    # usercount = team_users.count()

    # Count of projects involved
    projectno = projects.count()

    # All teams for dropdown or display
    teams = Teams.objects.all()

    context = {
        'user': user,
        'profile': profile,
        'issues_resolved': issues,
        'projects_involved': projectno,
        'billable_hours': billable_hours,
        'pto_taken': total_leave_taken,
        'teams': teams,
        'selected_team': selected_team,
        'usercount':usercount,
    }

    return render(request, 'teamdetail.html', context)
