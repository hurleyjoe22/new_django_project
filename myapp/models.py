from django.db import models

class SensorData(models.Model):
    ama2_distance = models.FloatField()
    ama3_distance = models.FloatField()
    ama4_distance = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Sensor Data at {self.timestamp}"
