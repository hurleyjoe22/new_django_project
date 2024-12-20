# Generated by Django 5.1.2 on 2024-10-12 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ama2_distance', models.FloatField()),
                ('ama3_distance', models.FloatField()),
                ('ama4_distance', models.FloatField()),
                ('temperature', models.FloatField()),
                ('humidity', models.FloatField()),
                ('timestamp', models.DateTimeField()),
            ],
        ),
    ]
