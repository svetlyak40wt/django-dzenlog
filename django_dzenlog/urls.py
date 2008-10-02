from django.conf.urls.defaults import *
from models import GeneralPost

info_dict = {
    'queryset': GeneralPost.objects.all(),
    'slug_field': 'hash'
}

urlpatterns = patterns('django.views.generic',
   (r'^(?P<slug>[a-z0-9-])/$', 'list_detail.object_detail', info_dict),
   (r'^/$', 'list_detail.object_list', info_dict),
)

