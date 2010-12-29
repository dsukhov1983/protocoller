from django.conf import settings

def maps_api_key(request):
    key = 'MAPS_API_KEY'
    return {key: getattr(settings, key, '')}
