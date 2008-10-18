from pdb import set_trace

from django.contrib.syndication.feeds import FeedDoesNotExist, Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

from models import GeneralPost, published
from utils import upcast
from views import get_tagged

def latest(cls, list_url_name):
    class PostsFeed(Feed):
        title = _('Latest posts')

        def get_object(self, bits):
            if len(bits) > 1:
                raise ObjectDoesNotExist
            if bits:
                return get_tagged(bits[0], published(cls.objects.all()))
            return None

        def link(self):
            return reverse(list_url_name)

        def items(self, obj):
            if obj:
                return obj[0][:20]
            return published(cls.objects.all())[:20]

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
