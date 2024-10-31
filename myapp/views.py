from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData
from django.utils import timezone
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
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Dashboard view
@login_required
def dashboard(request):
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
        try:
            # Parse the request data
            data = json.loads(request.body)
            relay_id = data.get('relayId')
            action = data.get('action')

            # Validate the presence of required fields
            if relay_id is None or action not in ['on', 'off']:
                return JsonResponse({'error': 'Missing or invalid fields'}, status=400)

            # Get the latest sensor data for the current date
            latest_data = SensorData.objects.filter(timestamp__date=timezone.now().date()).order_by('-timestamp').first()

            if latest_data:
                # Update relay state based on the relay_id
                if relay_id == 1:
                    latest_data.relay1 = action
                elif relay_id == 2:
                    latest_data.relay2 = action
                elif relay_id == 3:
                    latest_data.relay3 = action
                elif relay_id == 4:
                    latest_data.relay4 = action

                latest_data.save()  # Save changes to the database
                return JsonResponse({'message': 'Relay controlled successfully', 'relayId': relay_id, 'action': action})
            else:
                return JsonResponse({'error': 'No sensor data found for today'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        latest_data = SensorData.objects.order_by('-timestamp').first()

        if latest_data:
            data = {
                'relay1': latest_data.relay1,
                'relay2': latest_data.relay2,
                'relay3': latest_data.relay3,
                'relay4': latest_data.relay4
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No relay control data available'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# API view to handle data upload from Raspberry Pi
@csrf_exempt
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
                last_message=last_message if last_message else "No message",
                last_message_timestamp=last_message_timestamp if last_message_timestamp else None,
                timestamp=timestamp
            )

            return JsonResponse({'message': 'Data received successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error uploading sensor data: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# API view to handle setting relay timers
@csrf_exempt
def set_relay_timer(request):
    if request.method == 'POST':
        logger.info("Received request to set relay timer.")
        try:
            # Print raw request body for debugging purposes
            logger.debug(f"Raw request body: {request.body}")
            
            data = json.loads(request.body)
            relay_id = data.get('relayId')
            on_time = data.get('onTime')
            off_time = data.get('offTime')

            # Validate the presence of required fields
            if relay_id is None or on_time is None or off_time is None:
                logger.error(f"Missing fields in request: relayId={relay_id}, onTime={on_time}, offTime={off_time}")
                return JsonResponse({'error': 'Missing or invalid fields'}, status=400)

            # Log timer request details
            logger.info(f"Timer set for relay {relay_id}: ON for {on_time} seconds, OFF for {off_time} seconds")

            # Store the timer setting in the database
            latest_data = SensorData.objects.order_by('-timestamp').first()
            if latest_data:
                # Update the corresponding relay state to reflect a timer is active (could be a separate flag or state)
                if relay_id == 1:
                    latest_data.relay1 = f"timer-{on_time}-{off_time}"
                elif relay_id == 2:
                    latest_data.relay2 = f"timer-{on_time}-{off_time}"
                elif relay_id == 3:
                    latest_data.relay3 = f"timer-{on_time}-{off_time}"
                elif relay_id == 4:
                    latest_data.relay4 = f"timer-{on_time}-{off_time}"

                # Save the updated data
                latest_data.save()
                logger.info(f"Relay {relay_id} timer updated in the database.")

            return JsonResponse({'message': f'Timer set for relay {relay_id} successfully'}, status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received in request.")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error setting relay timer: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    logger.error(f"Invalid request method: {request.method}")
    return JsonResponse({'error': 'Invalid request method'}, status=405)