from django.conf import settings

#TODO make check for substrings
HAS_TAGGING = 'tagging' in settings.INSTALLED_APPS
HAS_MULTILINGUAL = 'multilingual' in settings.INSTALLED_APPS
