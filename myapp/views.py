from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData  # Import the model
from django.utils import timezone  # For handling timestamps
import logging

# Setup logger
logger = logging.getLogger(__name__)

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
    # Just render the dashboard, data will be populated via API
    return render(request, 'dashboard.html')

# API view to handle real-time sensor data request
def latest_sensor_data(request):
    latest_data = SensorData.objects.order_by('-timestamp').first()

    if latest_data:
        data = {
            'timestamp': latest_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ama2_distance': latest_data.ama2_distance,
            'ama3_distance': latest_data.ama3_distance,
            'ama4_distance': latest_data.ama4_distance,
            'temperature': latest_data.temperature,
            'humidity': latest_data.humidity,
            'relay1': latest_data.relay1,
            'relay2': latest_data.relay2,
            'relay3': latest_data.relay3,
            'relay4': latest_data.relay4,
            'last_message': latest_data.last_message,
            'last_message_timestamp': latest_data.last_message_timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_data.last_message_timestamp else None
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No data available'}, status=404)

# View to render the relay control page
@login_required
def relay_control_view(request):
    return render(request, 'relay_control.html')

# API view to handle relay control
@csrf_exempt
def control_relay(request):
    if request.method == 'POST':
        print("POST request received")  # Check if request reaches the view
        
        try:
            # Check if data is received
            data = json.loads(request.body)
            print("Received data:", data)  # Check what data is received
            
            relay_id = data.get('relayId')
            action = data.get('action')
            on_time = data.get('onTime')
            off_time = data.get('offTime')

            # Check if all fields are present
            if None in [relay_id, action, on_time, off_time]:
                print("Missing fields:", relay_id, action, on_time, off_time)
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            else:
                print(f"All fields present: relay_id={relay_id}, action={action}, on_time={on_time}, off_time={off_time}")

            # Get the latest sensor data for the current date, handling multiple records issue
            latest_data = SensorData.objects.filter(timestamp__date=timezone.now().date()).order_by('-timestamp').first()

            if latest_data:
                # Update relay timers based on the relay_id
                if relay_id == 1:
                    latest_data.relay1_on_time = on_time
                    latest_data.relay1_off_time = off_time
                elif relay_id == 2:
                    latest_data.relay2_on_time = on_time
                    latest_data.relay2_off_time = off_time
                elif relay_id == 3:
                    latest_data.relay3_on_time = on_time
                    latest_data.relay3_off_time = off_time
                elif relay_id == 4:
                    latest_data.relay4_on_time = on_time
                    latest_data.relay4_off_time = off_time

                latest_data.save()  # Save changes to the database
                print("Data saved to the database:", latest_data)  # Confirm data save

                return JsonResponse({'message': 'Relay controlled successfully', 'relay_id': relay_id, 'action': action, 'on_time': on_time, 'off_time': off_time})
            else:
                return JsonResponse({'error': 'No sensor data found for today'}, status=404)

        except json.JSONDecodeError:
            print("JSON Decode Error")  # Debug JSON error
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("Error occurred:", str(e))  # Print any exception for debugging
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        # Return the current state of the relays from the database
        latest_data = SensorData.objects.order_by('-timestamp').first()

        if latest_data:
            data = {
                'relay1_on_time': latest_data.relay1_on_time,
                'relay1_off_time': latest_data.relay1_off_time,
                'relay2_on_time': latest_data.relay2_on_time,
                'relay2_off_time': latest_data.relay2_off_time,
                'relay3_on_time': latest_data.relay3_on_time,
                'relay3_off_time': latest_data.relay3_off_time,
                'relay4_on_time': latest_data.relay4_on_time,
                'relay4_off_time': latest_data.relay4_off_time
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No relay control data available'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# API view to handle resetting all timers
@csrf_exempt
def reset_timers(request):
    if request.method == 'POST':
        try:
            # Get the latest sensor data record and reset relay timers
            latest_data = SensorData.objects.order_by('-timestamp').first()

            if latest_data:
                latest_data.relay1_on_time = 0
                latest_data.relay1_off_time = 0
                latest_data.relay2_on_time = 0
                latest_data.relay2_off_time = 0
                latest_data.relay3_on_time = 0
                latest_data.relay3_off_time = 0
                latest_data.relay4_on_time = 0
                latest_data.relay4_off_time = 0

                latest_data.save()  # Save the changes
                return JsonResponse({'message': 'All timers reset and relays turned off successfully'})
            else:
                logger.error('No data found to reset')
                return JsonResponse({'error': 'No data found to reset'}, status=404)

        except Exception as e:
            logger.error(f"Error resetting timers: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# API view to handle data upload from Raspberry Pi
@csrf_exempt  # Disable CSRF for API requests
def upload_sensor_data(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract sensor data from the request
            ama2_distance = data.get('ama2_distance')
            ama3_distance = data.get('ama3_distance')
            ama4_distance = data.get('ama4_distance')
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            relay1 = data.get('relay1')
            relay2 = data.get('relay2')
            relay3 = data.get('relay3')
            relay4 = data.get('relay4')
            last_message = data.get('last_message')
            last_message_timestamp = data.get('last_message_timestamp')
            timestamp = data.get('timestamp')

            # Validate that required data is present
            if None in [ama2_distance, ama3_distance, ama4_distance, temperature, humidity, relay1, relay2, relay3, relay4, timestamp]:
                logger.error('Missing required data fields')
                return JsonResponse({'error': 'Missing required data fields'}, status=400)

            # Save the data to the database
            SensorData.objects.create(
                ama2_distance=ama2_distance, 
                ama3_distance=ama3_distance,
                ama4_distance=ama4_distance, 
                temperature=temperature,
                humidity=humidity,
                relay1=relay1,
                relay2=relay2,
                relay3=relay3,
                relay4=relay4,
                last_message=last_message if last_message else "No message",  # Handle if last message is None
                last_message_timestamp=last_message_timestamp if last_message_timestamp else None,
                timestamp=timestamp
            )

            return JsonResponse({'message': 'Data received successfully'}, status=200)

        except json.JSONDecodeError:
            logger.error('Invalid JSON in sensor data upload')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error uploading sensor data: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
