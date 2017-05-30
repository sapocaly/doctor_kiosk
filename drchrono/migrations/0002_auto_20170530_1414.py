# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentprofile',
            name='notified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
    ]
