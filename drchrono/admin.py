from django.contrib import admin
from django.contrib.sessions.models import Session

from drchrono.models import Doctor, AppointmentProfile, Notification

admin.site.register(Doctor)
admin.site.register(AppointmentProfile)
admin.site.register(Notification)
admin.site.register(Session)
