from django.conf.urls.defaults import *
from models import GeneralPost

post_list = {
    'queryset': GeneralPost.objects.all(),
}

urlpatterns = patterns('django.views.generic',
   (r'^(?P<slug>[a-z0-9-])/$', 'list_detail.object_detail', post_list),
   (r'^$', 'list_detail.object_list', post_list),
)

