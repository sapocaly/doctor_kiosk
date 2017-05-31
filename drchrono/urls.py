from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

import views
from drchrono import api_views;

api_patterns = [
    url(r'^patient/$', api_views.PatientView.as_view(), name='patient'),
    url(r'^appointment/$', api_views.AppointmentView.as_view(), name='appointment'),
    url(r'^doctor/$', api_views.DoctorView.as_view(), name='doctor'),
    url(r'^appointment_list/$', api_views.AppointmentListView.as_view(), name='appointment_list'),
]

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='drchrono/index.html'), name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^kiosk/$', views.kiosk, name='kiosk'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^api/', include(api_patterns, namespace='api')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', admin.site.urls),
    # url(r'^socket/$', TemplateView.as_view(template_name='drchrono/socket.html'), name='socket'),
]
