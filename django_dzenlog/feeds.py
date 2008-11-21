from pdb import set_trace

from django.contrib.syndication.feeds import FeedDoesNotExist, Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404

from django_dzenlog.settings import HAS_TAGGING, RSS_LENGTH

from models import GeneralPost, published
from utils import upcast
from views import get_tagged, get_tags_by_slug

def latest(cls, list_url_name):
    class PostsFeed(Feed):
        title_template       = 'feeds/dzenlog_post_title.html'
        description_template = 'feeds/dzenlog_post_description.html'

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
                    params['tag'] = u'"%s"' % self.tags[0]
                    retval = _('%(site_name)s: latest %(post_type)s with tag %(tag)s')
                else:
                    params['tags'] = u', '.join(u'"%s"' % tag for tag in self.tags)
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
                items = obj[0][:RSS_LENGTH]
            else:
                items = published(cls.objects.all())[:RSS_LENGTH]
            return [obj.upcast() for obj in items]

        def item_pubdate(self, item):
            return item.publish_at

        def item_author_name(self, item):
            return item.author

        def item_categories(self, item):
            if HAS_TAGGING:
                return item.get_tags()
    return PostsFeed

def latest_comments(cls, comments_mixup, details_page_name):
    class CommentsFeed(comments_mixup, Feed):
        title_template       = 'feeds/dzenlog_comment_title.html'
        description_template = 'feeds/dzenlog_comment_description.html'

        def __init__(self, *args, **kwargs):
            self.object = None
            super(CommentsFeed, self).__init__(*args, **kwargs)

        title = _('%s: comments') % Site.objects.get_current().name

        def get_object(self, bits):
            if len(bits) != 1:
                return None
            self.object = get_object_or_404(cls, slug=bits[0])
            self.title = _(u'%(site_name)s: comments on "%(title)s"') % {
                'title': self.object.title,
                'site_name': Site.objects.get_current().name
            }
            return self.object

        def link(self):
            if self.object is None:
                return ''
            return reverse(details_page_name, kwargs=dict(slug=self.object.slug))

    return CommentsFeed

LatestPosts = latest(GeneralPost, 'dzenlog-post-list')

