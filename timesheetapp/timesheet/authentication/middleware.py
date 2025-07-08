from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from authentication.models import UserProfile

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path not in [reverse('force_change_password'), reverse('logout')]:
                try:
                    profile = request.user.userprofile
                except UserProfile.DoesNotExist:
                    profile = UserProfile.objects.create(user=request.user)

                # ✅ Handle missing timestamp
                if not profile.last_password_change or \
                   timezone.now() - profile.last_password_change > timedelta(days=90):

                    if not request.session.get('password_changed', False):
                        return redirect('force_change_password')

        return self.get_response(request)
