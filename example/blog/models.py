from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_dzenlog.models import GeneralPost

class TextPost(GeneralPost):
    body_detail_template = 'blog/text_post.html'
    feed_description_template = 'blog/text_feed_detail.html'

    body = models.TextField(_('Post\'s body'))


class LinkPost(GeneralPost):
    body_detail_template = 'blog/link_post.html'
    feed_description_template = 'blog/link_feed_detail.html'

    url = models.URLField(_('URL'), default='http://example.com', verify_exists=False)
    description = models.TextField(_('URL\'s description'), blank=True)

