import datetime

from django.db import models


class Doctor(models.Model):
    doctor_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    access_token = models.CharField(max_length=200)
    lifetime_waiting = models.DurationField(default=datetime.timedelta())
    lifetime_appointment_count = models.IntegerField(default=0)

    # this is a hard coded jsonfy method, to-do: use _getattr_ and __iter__ to optimize the code
    def as_json(self):
        return dict(doctor_id=self.doctor_id, first_name=self.first_name, last_name=self.last_name,
                    lifetime_waiting=self.lifetime_waiting.total_seconds(),
                    lifetime_appointment_count=self.lifetime_appointment_count)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class AppointmentProfile(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    app_id = models.IntegerField(primary_key=True)
    arrival_time = models.DateTimeField(auto_now_add=True)
    started_time = models.DateTimeField(null=True)
    completed_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.doctor.first_name + '@' + str(self.arrival_time)


class Notification(models.Model):
    message = models.CharField(max_length=200);
    notified = models.BooleanField(default=False);
    created_time = models.DateTimeField(auto_now_add=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

