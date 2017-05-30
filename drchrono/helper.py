import requests

from drchrono.models import Doctor

DRCHRONO_API_TEMPLATE = 'https://drchrono.com/api/{}'


class ProtoType(type):
    """
    A Helper Class For API Usage
    dynamically create method by name
    i.e: ApiHelper.get_appointments
        ApiHelper.patch_patients
    This saves time to code each method manually 
    """

    def __getattr__(cls, key):
        method_name, endpoint = key.split('_')
        method = getattr(requests, method_name)
        api_url = DRCHRONO_API_TEMPLATE.format(endpoint)

        def func(access_token, **kargs):
            headers = {'Authorization': 'Bearer {}'.format(access_token), }
            id = kargs.pop('id', None)
            url = api_url
            if id:
                if isinstance(id, list):
                    id = id[0]
                url += '/{}'.format(id)
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
    if 'doc_id' not in request.session:
        token = get_access_token(request)
        user_info = ApiHelper.get_users(token, id='current').json()
        doc_id = user_info['doctor']
        request.session['doc_id'] = doc_id
        doctor_info = ApiHelper.get_doctors(token, id=doc_id).json()
        doc, _ = Doctor.objects.get_or_create(first_name=doctor_info['first_name'], last_name=doctor_info['last_name'],
                                              doctor_id=doc_id)
        doc.access_token = token
        doc.save()


def get_access_token(request):
    auth = request.user.social_auth.get(provider='drchrono')
    return auth.extra_data['access_token']
