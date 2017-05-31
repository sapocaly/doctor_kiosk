from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from drchrono.helper import ApiHelper, get_access_token
from drchrono.models import Doctor, AppointmentProfile


class PatientView(View):
    def get(self, request):
        token = get_access_token(request)
        response = ApiHelper.get_patients(token, **request.GET)
        # if id is specified, then a response obj is returned, otherwise a recursive get will return a list of obj
        if 'id' in request.GET:
            return JsonResponse({'success': response.status_code == 200, 'data': response.json()})
        return JsonResponse({'success': True, 'data': response})

    def post(self, request):
        if 'id' not in request.POST:
            return JsonResponse({"success": False, 'error': 'id is not specified'})
        token = get_access_token(request)
        res = ApiHelper.patch_patients(token, **request.POST)
        if res.status_code != 204:
            return JsonResponse({"success": False, "error": res.json()})
        return JsonResponse({"success": True})


class AppointmentView(View):
    def post(self, request):
        if 'id' not in request.POST:
            return JsonResponse({"success": False, 'error': 'id is not specified'})
        token = get_access_token(request)
        res = ApiHelper.patch_appointments(token, **request.POST)
        if res.status_code != 204:
            return JsonResponse({"success": False, "error": res.json()})
        # generate or synchronize AppointmentProfile locally except when status is no show
        if 'status' in request.POST and request.POST['status'] != 'No Show':
            doctor = Doctor.objects.get(doctor_id=request.session['doc_id'])
            appointment, _ = AppointmentProfile.objects.get_or_create(doctor=doctor, app_id=request.POST['id'])
            status = request.POST['status']
            if status == 'In Session':
                appointment.started_time = timezone.now()
                doctor.lifetime_appointment_count += 1
                doctor.lifetime_waiting += (appointment.started_time - appointment.arrival_time)
                doctor.save()
            elif status == 'Complete':
                appointment.completed_time = timezone.now()
            appointment.save()
        return JsonResponse({"success": True})


class AppointmentListView(View):
    """
    today's appointment, come with patient info and local appointment profile
    """

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        token = get_access_token(request)
        appointments = ApiHelper.get_appointments(token, date=today, **request.GET)
        data = {'appointments': [], 'current': None}
        patients = ApiHelper.get_patients(token, rec=True)
        patient_table = {patient['id']: patient for patient in patients}
        for appointment in appointments:
            appointment['patient'] = patient_table[appointment['patient']]
            if appointment['status'] == 'Arrived':
                app = AppointmentProfile.objects.get(app_id=appointment['id'])
                appointment['time_waited'] = int((timezone.now() - app.arrival_time).total_seconds())
            elif appointment['status'] in ['In Session', 'Complete']:
                app = AppointmentProfile.objects.get(app_id=appointment['id'])
                appointment['time_waited'] = int((app.started_time - app.arrival_time).total_seconds())
            else:
                appointment['time_waited'] = None
            if appointment['status'] == 'In Session':
                data['current'] = appointment
            else:
                data['appointments'].append(appointment)
        return JsonResponse({'success': True, 'data': data})


class DoctorView(View):
    def get(self, request):
        doctor = Doctor.objects.get(doctor_id=request.session['doc_id'])
        return JsonResponse(doctor.as_json())
