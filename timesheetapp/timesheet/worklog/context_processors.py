from .models import MailNotification

def user_notifications(request):
    if request.user.is_authenticated:
        unseen_count = MailNotification.objects.filter(user=request.user, notification_seen=False).count()
        recent_notifications = MailNotification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'unseen_notification_count': unseen_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unseen_notification_count': 0,
        'recent_notifications': []
    }


