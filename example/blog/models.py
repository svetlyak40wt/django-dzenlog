from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body = models.TextField(_('Post\'s body'))

    def get_template(self):
        return 'blog/text_post.html'

class LinkPost(GeneralPost):
    url = models.URLField(_('URL'), default='http://example.com')
    description = models.TextField(_('URL\'s description'), blank=True)

    def get_template(self):
        return 'blog/link_post.html'

