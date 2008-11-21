from pdb import set_trace
from copy import deepcopy

from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf.urls.defaults import patterns
from django.conf import settings
from django.db.models import get_model
from django.db import connection

from models import GeneralPost
from django_dzenlog.settings import HAS_TAGGING
from feeds import latest, latest_comments

qn = connection.ops.quote_name

def create_patterns(model, url_prefix=None, comments_mixup = None):
    if isinstance(model, basestring):
        app_name, model_name = model.split('.')
        model = get_model(app_name, model_name)
        if model is None:
            raise Exception('Model %r not found in app %r' % (model_name, app_name))

    if url_prefix is None:
        url_prefix = ''
    else:
        if url_prefix and url_prefix[-1] != '/':
            url_prefix += '/'

    module_name = model._meta.module_name
    bytag_page_name = 'dzenlog-%s-bytag' % module_name
    tags_page_name = 'dzenlog-%s-tags' % module_name
    list_page_name = 'dzenlog-%s-list' % module_name
    all_comments_feed_page_name = 'dzenlog-%s-all-comments-feed' % module_name
    post_comments_feed_page_name = 'dzenlog-%s-post-comments-feed' % module_name
    details_page_name = 'dzenlog-%s-details' % module_name
    feeds_page_name = 'dzenlog-%s-feed' % module_name
    feeds_bytag_page_name = 'dzenlog-%s-bytag-feed' % module_name
    all_feeds_page_name = 'dzenlog-%s-feed' % GeneralPost._meta.module_name

    def feeds_url(page_name, fallback_page_name = None):
        '''Returns a function which returns function, which
           returns url with given view's name and params.'''
        def func(*args,**kwargs):
            def get_from_settings(name):
                if name is not None:
                    settings_param = name.upper().replace('-', '_')
                    return getattr(settings, settings_param, None)

            from_settings = get_from_settings(page_name) or get_from_settings(fallback_page_name)
            if from_settings is not None:
                return from_settings

            try:
                return reverse(page_name, args=args, kwargs=kwargs)
            except NoReverseMatch:
                if fallback_page_name:
                    return reverse(fallback_page_name, args=args, kwargs=kwargs)
                return ''
        return lambda: func

    extra_context = {
        'bytag_feeds_url': feeds_url(feeds_bytag_page_name),
        'feeds_url': feeds_url(feeds_page_name),
        'all_feeds_url': feeds_url(all_feeds_page_name, feeds_page_name),
    }

    if HAS_TAGGING:
        def bytag_url(tag_name):
            return reverse(bytag_page_name, kwargs=dict(slug=tag_name))
        extra_context['bytag_url'] = lambda: bytag_url
        extra_context['has_tagging'] = HAS_TAGGING

    if comments_mixup:
        extra_context['all_comments_feed_url'] = feeds_url(all_comments_feed_page_name)

    object_list = {
        'queryset': model._default_manager.all(),
        'template_name': model.list_template,
        'extra_context': extra_context,
    }

    object_info = deepcopy(object_list)
    object_info['template_name'] = model.detail_template
    if comments_mixup:
        object_info['extra_context']['post_comments_feed_url'] = feeds_url(post_comments_feed_page_name)

    feeds = {
        'rss': latest(model, list_page_name),
    }
    urlpatterns = patterns('django_dzenlog.views',
        (r'^%s(?P<slug>rss)(?P<param>)/$' % url_prefix, 'feed', {'feed_dict': feeds}, feeds_page_name),
        (r'^%s$' % url_prefix, 'post_list', object_list, list_page_name),
    )

    if comments_mixup:
        comments_feeds = {
            'rss': latest_comments(model, comments_mixup, details_page_name),
            'comments-rss': latest_comments(model, comments_mixup, details_page_name),
        }
        urlpatterns += patterns('django_dzenlog.views',
            (r'^%scomments/(?P<slug>rss)/$' % url_prefix, 'feed', {'feed_dict': comments_feeds}, all_comments_feed_page_name),
            (r'^%s(?P<param>[a-z0-9-]+)/(?P<slug>rss)/$' % url_prefix, 'feed', {'feed_dict': comments_feeds}, post_comments_feed_page_name),
        )

    if HAS_TAGGING:
        def calc_tag_cloud():
            from tagging.models import Tag, TaggedItem
            queryset = GeneralPost.objects.all()
            if model != GeneralPost:
                model_table = model._meta.db_table
                queryset = queryset.extra(
                                where=['id = %s.generalpost_ptr_id' % qn(model_table)],
                                tables=[model_table])
            ids = (obj.pk for obj in queryset)
            return Tag.objects.cloud_for_model(
                    GeneralPost,
                    min_count = getattr(settings, 'DZENLOG_TAGCLOUD_MINCOUNT', 0),
                    steps = getattr(settings, 'DZENLOG_TAGCLOUD_STEPS', 4),
                    filters = {'pk__in': ids}
                    )

        tag_cloud_data = {
            'template': model.tagcloud_template,
            'extra_context': object_list['extra_context'].copy(),
        }
        tag_cloud_data['extra_context']['object_list'] = calc_tag_cloud

        urlpatterns += patterns('django.views.generic',
            (r'^%sbytag/$' % url_prefix, 'simple.direct_to_template', tag_cloud_data, tags_page_name),
        )

        urlpatterns += patterns('django_dzenlog.views',
           (r'^%sbytag/(?P<slug>[^/]+)/$' % url_prefix, 'bytag', object_list, bytag_page_name),
        )

        urlpatterns += patterns('django_dzenlog.views',
            (r'^%sbytag/(?P<param>[^/]+)/(?P<slug>rss)/$' % url_prefix, 'feed', {'feed_dict': feeds}, feeds_bytag_page_name),
        )

    urlpatterns += patterns('django.views.generic',
        (r'^%s(?P<slug>[a-z0-9-]+)/$' % url_prefix, 'list_detail.object_detail', object_info, details_page_name),
    )
    return urlpatterns


urlpatterns = create_patterns('django_dzenlog.GeneralPost')
