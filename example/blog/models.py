from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body = models.TextField(_('Post\'s body'))

class LinkPost(GeneralPost):
    url = models.TextField(_('URL'))
    description = models.TextField(_('URL\'s description'))

