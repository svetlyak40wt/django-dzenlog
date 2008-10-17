from django.conf.urls.defaults import *
from models import GeneralPost
from feeds import latest

post_list = {
    'queryset': GeneralPost.objects.published(),
    'extra_context': {
        'bytag_page_name': 'dzenlog-post-bytag',
    }
}

feeds = {
    'all': latest(GeneralPost, 'dzenlog-post-list'),
}

urlpatterns = patterns('django_dzenlog.views',
   (r'^bytag/(?P<slug>.+)/$', 'bytag', post_list, 'dzenlog-post-bytag'),
)

urlpatterns += patterns('django.views.generic',
   (r'^(?P<slug>[a-z0-9-]+)/$', 'list_detail.object_detail', post_list, 'dzenlog-post-details'),
   (r'^$', 'list_detail.object_list', post_list, 'dzenlog-post-list'),
)

urlpatterns += patterns('django.contrib.syndication.views',
   (r'^rss/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}, 'dzenlog-feeds'),
)

