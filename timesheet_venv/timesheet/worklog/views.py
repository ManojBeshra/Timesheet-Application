from django.shortcuts import render
from task.models import priority_type, ticket
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Create your views here.

def worklog(request):

    priority = priority_type.objects.all()
    users = User.objects.all()
    tickets = ticket.objects.all()
    return render(request, 'worklog.html', {'priority': priority, 'tickets': tickets, 'users': users})



@login_required
@csrf_exempt
def request_review(request):
    if request.method == 'POST':
        try:
            
            date_requested = request.POST.get('date')
            assigned_users = request.POST.getlist('assigneduserlist[]') # Get multiple users
            operational_notes = request.POST.get('shortdescriptionarea')
           

            # Create new request
            new_request = request(
                date_requested=date_requested,
                operational_notes=operational_notes,
            )

            new_request.save()


            # Assign multiple users
            assigned_user_objs = User.objects.filter(id__in=assigned_users)
            new_request.assigned_to.set(assigned_user_objs)  # Use `.set()` for ManyToManyField

            return JsonResponse({"success": True, "message": "Request added successfully!"})
        except Exception as e:
            print(f"Error: {e}")  # Debugging
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
