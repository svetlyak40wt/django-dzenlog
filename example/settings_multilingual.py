from settings import *

DATABASE_NAME = 'dzenlog_m'

INSTALLED_APPS += ('multilingual',)

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)

DEFAULT_LANGUAGE = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'multilingual.context_processors.multilingual',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'multilingual.middleware.DefaultLanguageMiddleware',
)
