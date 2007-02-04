from django.conf import settings

def media_url(request):
    """
    Return media URL for all static data
    """
    return {'media_url': settings.MEDIA_URL}
