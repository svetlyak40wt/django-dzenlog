from django.conf.urls.defaults import *
from models import TextPost, LinkPost

text_list = {
    'queryset': TextPost.objects.all(),
    'template_name': 'django_dzenlog/generalpost_list.html',
}

link_list = {
    'queryset': LinkPost.objects.all(),
    'template_name': 'django_dzenlog/generalpost_list.html',
}

text_info = text_list.copy()
text_info['template_name'] = 'django_dzenlog/generalpost_detail.html'
link_info = link_list.copy()
link_info['template_name'] = 'django_dzenlog/generalpost_detail.html'


urlpatterns = patterns('django.views.generic',
   (r'^text/(?P<slug>[a-z0-9-]+)/$', 'list_detail.object_detail', text_info, 'blog-text-details'),
   (r'^link/(?P<slug>[a-z0-9-]+)/$', 'list_detail.object_detail', link_info, 'blog-link-details'),

   (r'^text/$', 'list_detail.object_list', text_list, 'blog-text-list'),
   (r'^link/$', 'list_detail.object_list', link_list, 'blog-link-list'),
)
