from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Default to login page
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Redirect to login page after logout
    path('force-change-password/', views.force_change_password, name='force_change_password'),
    path('manual-change-password/', views.public_password_change_view, name='manual_change_password'),
]
