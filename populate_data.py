import os
from random import shuffle, randint

from django.utils import timezone
from django.utils.timezone import template_localtime, localtime

from drchrono.models import AppointmentProfile, Doctor

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drchrono.settings')

import django

django.setup()
from drchrono.helper import ApiHelper

# from faker import Faker

# fakegen = Faker()

"""
doctor	integer	required	Doctor ID
duration	integer	required* (see note)	Length of the appointment in minutes. Optional if profile is provided.
exam_room	integer	required	Index of the exam room that this appointment occurs in. See /api/offices.
office	integer	required	Office ID
patient	integer or null	required	ID of this appointment's patient. Breaks have a null patient field.
scheduled_time	timestamp	required	The starting time of the appointment
"""

DOCTOR = 133464
OFFICE = 141500
PATIENT = [65249162]
DURATIONS = [30, 45, 50, 37]
TOKEN = '7kHtQqk2hsKhrmuDsj4aup3dWV2l2K'


def generate_api_appointments():
    now = timezone.now()
    for i in range(9, 19):
        shuffle(PATIENT)
        shuffle(DURATIONS)
        scheduled_time = now.replace(hour=i, minute=0)
        print ApiHelper.post_appointments(TOKEN, doctor=DOCTOR, duration=DURATIONS[0], exam_room=randint(1, 8),
                                          office=OFFICE,
                                          status='Confirmed',
                                          patient=PATIENT[0],
                                          scheduled_time=scheduled_time).content


def clean_appointment_profiles():
    AppointmentProfile.objects.all().delete()


def clean_doctors():
    Doctor.objects.all().delete()


def reset_all_appointment():
    today = localtime(timezone.now()).date()
    today_apps = ApiHelper.get_appointments(TOKEN, date=today)
    app_ids = [app['id'] for app in today_apps]
    for id in app_ids:
        ApiHelper.patch_appointments(TOKEN, id=id, status='Confirmed')


if __name__ == '__main__':
    reset_all_appointment()
