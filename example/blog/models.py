from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body = models.TextField(_('Post\'s body'))

    def _get_template(self):
        return 'blog/text_post.html'

    def _get_absolute_url(self):
        return ('blog-text-details', (), dict(slug=self.slug))


class LinkPost(GeneralPost):
    url = models.URLField(_('URL'), default='http://example.com')
    description = models.TextField(_('URL\'s description'), blank=True)

    def _get_template(self):
        return 'blog/link_post.html'

    def _get_absolute_url(self):
        return ('blog-link-details', (), dict(slug=self.slug))

