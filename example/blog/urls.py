from django_dzenlog.urls import create_patterns

urlpatterns = create_patterns('blog.TextPost', 'text')
urlpatterns += create_patterns('blog.LinkPost', u'links')
