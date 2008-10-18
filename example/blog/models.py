from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body = models.TextField(_('Post\'s body'))

    def _get_template(self):
        return 'blog/text_post.html'
TextPost._meta.translation_model = GeneralPost._meta.translation_model


class LinkPost(GeneralPost):
    url = models.URLField(_('URL'), default='http://example.com', verify_exists=False)
    description = models.TextField(_('URL\'s description'), blank=True)

    def _get_template(self):
        return 'blog/link_post.html'
LinkPost._meta.translation_model = GeneralPost._meta.translation_model

