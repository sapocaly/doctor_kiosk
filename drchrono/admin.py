from django.contrib import admin
from django.contrib.sessions.models import Session

from drchrono.models import Doctor, AppointmentProfile

admin.site.register(Doctor)
admin.site.register(AppointmentProfile)
admin.site.register(Session)
