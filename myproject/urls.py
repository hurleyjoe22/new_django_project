from django.contrib import admin
from django.urls import path
from myapp import views  # Import the views from your app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),  # This makes the login page the default
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard after login
]
