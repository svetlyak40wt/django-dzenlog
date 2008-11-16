from django.conf import settings

HAS_TAGGING = 'tagging' in settings.INSTALLED_APPS
RSS_LENGTH = getattr(settings, 'DZENLOG_RSS_LENGTH', 20)
