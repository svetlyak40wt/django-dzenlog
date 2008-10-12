from django.contrib.syndication.feeds import FeedDoesNotExist, Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

from models import GeneralPost
from utils import upcast

def latest(cls, list_url_name):
    class PostsFeed(Feed):
        title = _('Latest posts')

        def link(self):
            return reverse(list_url_name)

        def items(self):
            return cls.objects.published()[:20]

        def item_pubdate(self, item):
            return item.publish_at

        def item_author_name(self, item):
            return item.author

        def item_categories(self, item):
            if settings.HAS_TAGGING:
                from tagging.models import Tag
                return Tag.objects.get_for_object(upcast(item))
    return PostsFeed

LatestPosts = latest(GeneralPost, 'dzenlog-post-list')
