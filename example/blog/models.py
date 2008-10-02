from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body = models.TextField(_('Post\'s body'))

    def render(self):
        return 'Text post with title \'%s\' and body:\n %s' % (self.title, self.body)

class LinkPost(GeneralPost):
    url = models.URLField(_('URL'), default='http://example.com')
    description = models.TextField(_('URL\'s description'), blank=True)

