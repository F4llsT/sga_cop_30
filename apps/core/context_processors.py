from django.conf import settings

def onesignal(request):
    """Expose OneSignal App ID to templates as ONESIGNAL_APP_ID."""
    return {
        'ONESIGNAL_APP_ID': getattr(settings, 'ONESIGNAL_APP_ID', ''),
    }
