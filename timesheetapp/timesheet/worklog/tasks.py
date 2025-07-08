import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import MailNotification
from datetime import date, timedelta
from celery import shared_task

# Setting up logger
logger = logging.getLogger(__name__)

def get_start_of_week():
    today = date.today()
    return today - timedelta(days=today.weekday())  # Monday


@shared_task(bind=True, max_retries=3)
def send_weekly_email(self):
    try:
        week_start_date = get_start_of_week()

        subject = 'Weekly Worklog Update'
        message = 'Here is your weekly update. Please review your worklog.'
        recipient_emails = ['neeteshzung931@gmail.com']

        # Log the email sending info
        logger.info(f"Sending weekly email to: {recipient_emails}")
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_emails, fail_silently=False)

        notifications = []
        for email in recipient_emails:
            user = User.objects.filter(email=email).first()
            if user:
                notif_type = 'ADMIN_MAIL' if email == 'neeteshzung931@gmail.com' else 'USER_MAIL'
                notif_msg = "You need to review the user worklogs for this week." if notif_type == 'ADMIN_MAIL' else "Please review your worklog for this week."

                # Make sure week_start_date is being passed
                notifications.append(MailNotification(
                    user=user,
                    message=notif_msg,
                    created_at=week_start_date,  # Passing week_start_date here
                    week_start_date=week_start_date,  # Ensure the field is filled
                ))

        # Bulk create notifications
        MailNotification.objects.bulk_create(notifications)

        logger.info(f"Notifications created: {len(notifications)}")

        return "Emails and notifications sent successfully."

    except Exception as e:
        logger.error(f"Error in send_weekly_email: {e}")
        raise self.retry(exc=e, countdown=60)
