from django.conf import settings

from . import models
from . import common


def maps_api_key(request):
    key = 'MAPS_API_KEY'
    return {key: getattr(settings, key, '')}


def compare_list(request):
    compare_set = request.session.get(common.COMPARE_LIST_SESSION_KEY, set())
    persons = list(models.Person.objects.filter(id__in=compare_set))
    return dict(compare_list=persons)

