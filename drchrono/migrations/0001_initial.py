# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentProfile',
            fields=[
                ('app_id', models.IntegerField(serialize=False, primary_key=True)),
                ('arrival_time', models.DateTimeField(auto_now_add=True)),
                ('started_time', models.DateTimeField(null=True)),
                ('completed_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('doctor_id', models.IntegerField(serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('access_token', models.CharField(max_length=200)),
                ('lifetime_waiting', models.DurationField(default=datetime.timedelta(0))),
                ('lifetime_appointment_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='appointmentprofile',
            name='doctor',
            field=models.ForeignKey(to='drchrono.Doctor'),
        ),
    ]
