from pdb import set_trace

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from django.db.models import get_model

from models import GeneralPost, published
from feeds import latest

def create_patterns(model, url_prefix=None):
    if isinstance(model, basestring):
        app_name, model_name = model.split('.')
        model = get_model(app_name, model_name)

    if url_prefix is None:
        url_prefix = ''
    else:
        if url_prefix[-1] != '/':
            url_prefix += '/'

    module_name = model._meta.module_name
    bytag_page_name = 'dzenlog-%s-bytag' % module_name
    list_page_name = 'dzenlog-%s-list' % module_name
    details_page_name = 'dzenlog-%s-details' % module_name
    feeds_page_name = 'dzenlog-%s-feeds' % module_name

    all_feeds_page_name = 'dzenlog-%s-feeds' % GeneralPost._meta.module_name

    def bytag_url(tag_name):
        return reverse(bytag_page_name, kwargs=dict(slug=tag_name))

    def feeds_url(url):
        return reverse(feeds_page_name, kwargs=dict(url=url))

    def all_feeds_url(url):
        return reverse(all_feeds_page_name, kwargs=dict(url=url))

    object_list = {
        'queryset': published(model._default_manager.all()),
        'template_name': 'django_dzenlog/generalpost_list.html',
        'extra_context': {
            'bytag_url': lambda: bytag_url,
            'feeds_url': lambda: feeds_url,
            'all_feeds_url': lambda: all_feeds_url,
        }
    }

    object_info = object_list.copy()
    object_info['template_name'] = 'django_dzenlog/generalpost_detail.html'

    feeds = {
        'rss': latest(model, list_page_name),
    }
    urlpatterns = patterns('django_dzenlog.views',
       (r'^%sbytag/(?P<slug>.+)/$' % url_prefix, 'bytag', object_list, bytag_page_name),
    )
    urlpatterns += patterns('django.views.generic',
        (r'^%s(?P<slug>[a-z0-9-]+)/$' % url_prefix, 'list_detail.object_detail', object_info, details_page_name),
        (r'^%s$' % url_prefix, 'list_detail.object_list', object_list, list_page_name),
    )
    # feeds
    urlpatterns += patterns('django.contrib.syndication.views',
        (r'^%sfeeds/(?P<url>.*)/$' % url_prefix, 'feed', {'feed_dict': feeds}, feeds_page_name),
    )
    return urlpatterns


urlpatterns = create_patterns('django_dzenlog.GeneralPost')
