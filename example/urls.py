from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^', include('blog.urls')), # place this before dzenlog's urls if the have one root.
    (r'^', include('django_dzenlog.urls')),
)

