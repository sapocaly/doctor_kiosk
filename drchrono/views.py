from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from drchrono.helper import check_in_session
from drchrono.models import Doctor


@login_required
def dashboard(request):
    check_in_session(request)
    doc = Doctor.objects.get(doctor_id=request.session['doc_id'])
    return render(request, 'drchrono/dashboard.html', {'doctor': doc})


@login_required
def kiosk(request):
    check_in_session(request)
    return render(request, 'drchrono/kiosk.html')


def log_out(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect(reverse('index'))
