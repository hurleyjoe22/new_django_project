# Generated by Django 5.1.2 on 2024-10-27 02:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_sensordata_relay1_off_time_sensordata_relay1_on_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensordata',
            name='relay1_off_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay1_on_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay2_off_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay2_on_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay3_off_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay3_on_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay4_off_time',
        ),
        migrations.RemoveField(
            model_name='sensordata',
            name='relay4_on_time',
        ),
    ]
