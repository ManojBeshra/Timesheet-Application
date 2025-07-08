from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from authentication.models import UserProfile
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'registration/dashboard.html', {'section':'dashboard'})

@login_required
def force_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            request.user.userprofile.last_password_change = timezone.now()
            request.user.userprofile.save()
            request.session['password_changed'] = True
            messages.success(request, "Password changed successfully.")
            return redirect('login')  
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'force_change_password.html', {'form': form})

created = 0
for user in User.objects.all():
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)  # Don't set last_password_change
        created += 1

print(f"Backfill complete: {created} missing UserProfiles created.")

# authentication/views.py

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import UserProfile
from django.contrib import messages

def public_password_change_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not all([username, old_password, new_password1, new_password2]):
            messages.error(request, "All fields are required.")
            return redirect('manual_change_password')

        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('manual_change_password')

        user = authenticate(username=username, password=old_password)
        if user is not None:
            user.password = make_password(new_password1)
            user.save()

            # Update profile password change timestamp
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.last_password_change = timezone.now()
            profile.save()

            messages.success(request, "Password changed successfully. You can now log in.")
            # return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('manual_change_password')

    return render(request, 'public_change_password.html')
