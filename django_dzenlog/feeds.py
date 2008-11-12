from pdb import set_trace

from django.contrib.syndication.feeds import FeedDoesNotExist, Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
import settings

from models import GeneralPost, published
from utils import upcast
from views import get_tagged, get_tags_by_slug

def latest(cls, list_url_name):
    class PostsFeed(Feed):
        def __init__(self, *args, **kwargs):
            self.tags = None
            super(PostsFeed, self).__init__(*args, **kwargs)

        def title(self):
            params = {
                'site_name': Site.objects.get_current().name,
                'post_type': cls._meta.verbose_name_plural.lower(),
            }
            retval = _('%(site_name)s: latest %(post_type)s')

            if self.tags:
                if len(self.tags) == 1:
                    params['tag'] = '"%s"' % self.tags[0]
                    retval = _('%(site_name)s: latest %(post_type)s with tag %(tag)s')
                else:
                    params['tags'] = ', '.join('"%s"' % tag for tag in self.tags)
                    retval = _('%(site_name)s: latest %(post_type)s with tags %(tags)s')
            return retval % params

        def get_object(self, bits):
            if len(bits) > 1:
                raise ObjectDoesNotExist
            if bits:
                self.tags = get_tags_by_slug(bits[0])
                return get_tagged(bits[0], published(cls.objects.all()), tags=self.tags)
            return None

        def categories(self, obj):
            if obj and len(obj) == 2:
                return obj[1]

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
                return item.get_tags()
    return PostsFeed

LatestPosts = latest(GeneralPost, 'dzenlog-post-list')
