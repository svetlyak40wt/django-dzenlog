from datetime import datetime

from django.contrib.syndication.feeds import FeedDoesNotExist, Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

from models import GeneralPost
from utils import upcast

class LatestPosts(Feed):
    title = _('Latest posts')

    def link(self):
        return reverse('dzenlog-post-list')

    def items(self):
        return GeneralPost.objects.filter(publish_at__lte=datetime.today())[:20]

    def item_pubdate(self, item):
        return item.publish_at

    def item_author_name(self, item):
        return item.author

    def item_categories(self, item):
        if settings.HAS_TAGGING:
            from tagging.models import Tag
            return Tag.objects.get_for_object(upcast(item))

