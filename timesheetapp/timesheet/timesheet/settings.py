from celery.schedules import crontab    
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vcte=l$5q=&e$@1pdgp$3%34-3md^vpn1xv04=!mn0+-39dhc*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS = [
    "*",
    "localhost",
    "127.0.0.1",
    "https://sub.glaciersystemsinc.com",
    "timesheet.glaciersystemsinc.com",
    "https://timesheet.glaciersystemsinc.com",
    "timesheet1.glaciersystemsinc.com",
    "https://timesheet1.glaciersystemsinc.com",
    "http://timesheet1.glaciersystemsinc.com",
    "http://glaciersystemstimesheet.com",
    "http://timesheet.glaciersystemsinc.com:8003/",
    "http://timesheet.glaciersystemsinc.com:8002/",
    "https://hyena-fit-ibex.ngrok-free.app",
    
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #created apps
    'authentication.apps.AuthenticationConfig',
    # 'authentication',
    'worklog',
    # 'attendance',
    'attendance.apps.AttendanceConfig',
    'task',
    'user',
    'company',
    'customer',
    'report',
    'invoice',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #new
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'authentication.middleware.ForcePasswordChangeMiddleware',

]

ROOT_URLCONF = 'timesheet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'timesheet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = BASE_DIR /'production'
STATIC_URL = 'static/'

#new added
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#for login , logout
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

#To Send an Email
# from decouple import config
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False  # Ensure this is False when using TLS
# EMAIL_HOST_USER = config("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = "beshra9988@gmail.com"
EMAIL_HOST_PASSWORD = "hqgkyulhmtnpvggq"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'send-weekly-email': {
        'task': 'worklog.tasks.send_weekly_email',
        'schedule': crontab(hour=10, minute=15, day_of_week='wednesday'),  # Wed at 12:12 PM
    },
    'send-weekly-worklog-review-reminder-to-admin': { 
        'task': 'worklog.tasks.send_worklog_review_reminder_to_admin',
        'schedule': crontab(hour=12, minute=15, day_of_week='wednesday'),  # Wed at 12:30 PM
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

CSRF_TRUSTED_ORIGINS = [
    "https://sub.glaciersystemsinc.com",
    "https://timesheet1.glaciersystemsinc.com",
    "http://timesheet1.glaciersystemsinc.com",
    "http://glaciersystemstimesheet.com",
    "http://timesheet.glaciersystemsinc.com:8003/",
    "http://timesheet.glaciersystemsinc.com:8002/",


]

# To store the profile picture
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
