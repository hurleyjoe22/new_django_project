# Generated by Django 5.1.2 on 2024-10-16 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='last_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='last_message_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='relay1',
            field=models.CharField(default='off', max_length=5),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='relay2',
            field=models.CharField(default='off', max_length=5),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='relay3',
            field=models.CharField(default='off', max_length=5),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='relay4',
            field=models.CharField(default='off', max_length=5),
        ),
    ]