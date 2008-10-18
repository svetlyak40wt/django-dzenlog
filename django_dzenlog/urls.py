from pdb import set_trace

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns
from django.db.models import get_model

from models import GeneralPost, published
from settings import HAS_TAGGING
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
    tags_page_name = 'dzenlog-%s-tags' % module_name
    list_page_name = 'dzenlog-%s-list' % module_name
    details_page_name = 'dzenlog-%s-details' % module_name
    feeds_page_name = 'dzenlog-%s-feeds' % module_name
    feeds_bytag_page_name = 'dzenlog-%s-bytag-feeds' % module_name
    all_feeds_page_name = 'dzenlog-%s-feeds' % GeneralPost._meta.module_name

    #TODO use DRY principle
    def feeds_url(*args,**kwargs):
        kwargs.setdefault('param', '')
        return reverse(feeds_page_name, args=args, kwargs=kwargs)

    def bytag_feeds_url(*args,**kwargs):
        kwargs.setdefault('param', '')
        return reverse(feeds_bytag_page_name, args=args, kwargs=kwargs)

    def all_feeds_url(*args, **kwargs):
        kwargs.setdefault('param', '')
        return reverse(all_feeds_page_name, args=args, kwargs=kwargs)

    extra_context = {
        'feeds_url': lambda: feeds_url,
        'all_feeds_url': lambda: all_feeds_url,
    }

    if HAS_TAGGING:
        def bytag_url(tag_name):
            return reverse(bytag_page_name, kwargs=dict(slug=tag_name))
        extra_context['bytag_url'] = lambda: bytag_url

    object_list = {
        'queryset': published(model._default_manager.all()),
        'template_name': 'django_dzenlog/generalpost_list.html',
        'extra_context': extra_context,
    }

    object_info = object_list.copy()
    object_info['template_name'] = 'django_dzenlog/generalpost_detail.html'

    feeds = {
        'rss': latest(model, list_page_name),
    }
    urlpatterns = patterns('django_dzenlog.views',
        (r'^%s(?P<slug>rss)(?P<param>)/$' % url_prefix, 'feed', {'feed_dict': feeds}, feeds_page_name),
    )

    if HAS_TAGGING:
        bytag_object_list = object_list.copy()
        bytag_object_list['extra_context'] = object_list['extra_context'].copy()
        bytag_object_list['extra_context']['feeds_url'] = lambda: bytag_feeds_url

        from tagging.models import Tag, TaggedItem
        tag_list = {
            'queryset': Tag.objects.all(),
            'template_name': 'django_dzenlog/tag_list.html',
            'extra_context': extra_context,
        }

        urlpatterns += patterns('django.views.generic',
            (r'^%sbytag/$' % url_prefix, 'list_detail.object_list', tag_list, tags_page_name),
        )
        urlpatterns += patterns('django_dzenlog.views',
           (r'^%sbytag/(?P<slug>[^/]+)/$' % url_prefix, 'bytag', bytag_object_list, bytag_page_name),
        )
        urlpatterns += patterns('django_dzenlog.views',
            (r'^%sbytag/(?P<param>[^/]+)/(?P<slug>rss)/$' % url_prefix, 'feed', {'feed_dict': feeds}, feeds_bytag_page_name),
        )

    urlpatterns += patterns('django.views.generic',
        (r'^%s(?P<slug>[a-z0-9-]+)/$' % url_prefix, 'list_detail.object_detail', object_info, details_page_name),
        (r'^%s$' % url_prefix, 'list_detail.object_list', object_list, list_page_name),
    )
    return urlpatterns


urlpatterns = create_patterns('django_dzenlog.GeneralPost')
