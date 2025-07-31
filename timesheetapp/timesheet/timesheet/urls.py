from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('task/', include('task.urls')),
    path('worklog/', include('worklog.urls')),
    path('attendance/', include('attendance.urls')),
    path('report/', include('report.urls')),
    path('user/', include('user.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)