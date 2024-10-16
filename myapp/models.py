from django.db import models

class SensorData(models.Model):
    ama2_distance = models.FloatField()
    ama3_distance = models.FloatField()
    ama4_distance = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()

    # New fields for relay states with a default value of 'off'
    relay1 = models.CharField(max_length=5, default='off')  # 'on' or 'off'
    relay2 = models.CharField(max_length=5, default='off')
    relay3 = models.CharField(max_length=5, default='off')
    relay4 = models.CharField(max_length=5, default='off')

    # Last text message and timestamp fields
    last_message = models.TextField(null=True, blank=True)
    last_message_timestamp = models.DateTimeField(null=True, blank=True)

    # The timestamp for the sensor data
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Sensor Data at {self.timestamp}"

