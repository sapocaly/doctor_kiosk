import requests

from drchrono.models import Doctor

DRCHRONO_API_TEMPLATE = 'https://drchrono.com/api/{}'


class ProtoType(type):
    """
    A Helper Class For API Usage
    dynamically create method by name
    """

    def __getattr__(cls, key):
        """
        method getter for the helper
        @param key: method name i.e: get_appointments, patch_patients, post_appointments
        @return: generated method
        """
        action_type, endpoint = key.split('_')
        method = getattr(requests, action_type)
        api_url = DRCHRONO_API_TEMPLATE.format(endpoint)

        def func(access_token, **kargs):
            headers = {'Authorization': 'Bearer {}'.format(access_token), }
            id = kargs.pop('id', None)
            url = api_url
            if id:
                url += '/{}'.format(id[0] if isinstance(id, list) else id)
            elif method == requests.get:
                results = []
                while url:
                    content = requests.get(url, kargs, headers=headers).json()
                    results.extend(content['results'])
                    url = content['next']
                return results
            return method(url, kargs, headers=headers)

        return func


class ApiHelper:
    __metaclass__ = ProtoType


def check_in_session(request):
    """
    add doc_id to session, create doctor obj if necessary
    """
    if 'doc_id' not in request.session:
        token = get_access_token(request)
        user_info = ApiHelper.get_users(token, id='current').json()
        doc_id = user_info['doctor']
        request.session['doc_id'] = doc_id
        doctor_info = ApiHelper.get_doctors(token, id=doc_id).json()
        doc, _ = Doctor.objects.get_or_create(doctor_id=doc_id)
        doc.access_token = token
        # in case name changed
        doc.first_name = doctor_info['first_name']
        doc.last_name = doctor_info['last_name']
        doc.save()


def get_access_token(request):
    # doesn't work when user is logged in as superuser
    auth = request.user.social_auth.get(provider='drchrono')
    return auth.extra_data['access_token']
