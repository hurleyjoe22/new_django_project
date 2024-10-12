from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData  # Import the model

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})  # Render the login form

# Dashboard view
@login_required
def dashboard(request):
    # Get the latest sensor data from the database
    latest_data = SensorData.objects.order_by('-timestamp').first()

    context = {
        'timestamp': latest_data.timestamp if latest_data else 'No data',
        'ama2_distance': latest_data.ama2_distance if latest_data else 'No data',
        'ama3_distance': latest_data.ama3_distance if latest_data else 'No data',
        'ama4_distance': latest_data.ama4_distance if latest_data else 'No data',
        'temperature': latest_data.temperature if latest_data else 'No data',
        'humidity': latest_data.humidity if latest_data else 'No data'
    }

    return render(request, 'dashboard.html', context)  # Render the dashboard page with sensor data

# API view to handle data upload from Raspberry Pi
@csrf_exempt  # Disable CSRF for API requests
def upload_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ama2_distance = data.get('ama2_distance')
            ama3_distance = data.get('ama3_distance')
            ama4_distance = data.get('ama4_distance')
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            timestamp = data.get('timestamp')

            # Save the data to the database
            SensorData.objects.create(
                ama2_distance=ama2_distance, 
                ama3_distance=ama3_distance,
                ama4_distance=ama4_distance, 
                temperature=temperature,
                humidity=humidity, 
                timestamp=timestamp
            )

            return JsonResponse({'message': 'Data received successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
