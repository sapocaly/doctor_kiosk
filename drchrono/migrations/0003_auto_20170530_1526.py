# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0002_auto_20170530_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=200)),
                ('notified', models.BooleanField(default=False)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(to='drchrono.Doctor')),
            ],
        ),
        migrations.RemoveField(
            model_name='appointmentprofile',
            name='notified',
        ),
    ]
