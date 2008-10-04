from django.conf.urls.defaults import *
from models import GeneralPost
from feeds import LatestPosts

post_list = {
    'queryset': GeneralPost.objects.all(),
}

feeds = {
    'all': LatestPosts,
}

urlpatterns = patterns('django.views.generic',
   (r'^(?P<slug>[a-z0-9-]+)/$', 'list_detail.object_detail', post_list, 'dzenlog-post-details'),
   (r'^$', 'list_detail.object_list', post_list, 'dzenlog-post-list'),
)

urlpatterns += patterns('django.contrib.syndication.views',
   (r'^rss/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}, 'dzenlog-feeds'),
)

