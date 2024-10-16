from django.contrib import admin
from django.urls import path
from myapp import views  # Import your views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin page access
    path('', views.login_view, name='login'),  # Login page as the default view
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard after login
    path('api/latest-sensor-data/', views.latest_sensor_data, name='latest_sensor_data'),
    path('api/upload-sensor-data/', views.upload_sensor_data, name='upload_sensor_data'),  # New API route
    path('relay-control/', views.relay_control_view, name='relay_control'),  # URL for relay control page
    path('api/control-relay/', views.control_relay, name='control_relay'),  # API route for controlling relays
    path('api/reset-timers/', views.reset_timers, name='reset_timers'),  # API route for resetting timers
]
