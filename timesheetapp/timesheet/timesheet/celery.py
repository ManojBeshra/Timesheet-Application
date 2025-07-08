from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timesheet.settings')

app = Celery('timesheet')

app.conf.update(
    CELERY_WORKER_POOL='solo',
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
