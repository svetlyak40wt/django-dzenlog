from settings import *

INSTALLED_APPS = tuple(app for app in INSTALLED_APPS if app != 'tagging')
