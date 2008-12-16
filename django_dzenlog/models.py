'''
Inherit your own models from GeneralPost class
and define there application specific fieldd.
'''

import logging
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

import settings
import signals
from pdb import set_trace

if settings.HAS_TAGGING:
    from tagging.fields import TagField
    from tagging.models import Tag


from utils import upcast

def published(queryset):
    'Filter out not published posts.'
    return queryset.filter(publish_at__lte=datetime.now())

class GeneralPost(models.Model):
    '''Base class for blog posts.'''
    # templates
    list_template             = 'django_dzenlog/list.html'
    detail_template           = 'django_dzenlog/detail.html'
    tagcloud_template         = 'django_dzenlog/tagcloud.html'
    body_detail_template      = 'django_dzenlog/body_detail.html'
    body_list_template        = 'django_dzenlog/body_list.html'
    feed_title_template       = 'django_dzenlog/feed_title.html'
    feed_description_template = 'django_dzenlog/feed_description.html'

    # fields
    author      = models.ForeignKey(User, verbose_name = _('Author'))
    title       = models.CharField(_('Title'), max_length=100)
    slug        = models.SlugField(_('Slug title'), max_length=100, unique=True)
    created_at  = models.DateTimeField(_('Create date'),
                                       blank=True, editable=False)
    updated_at  = models.DateTimeField(_('Update date'),
                                       blank=True, editable=False)
    publish_at  = models.DateTimeField(_('Publish date'), blank=True, null=True)
    comments_on = models.BooleanField(_('Comments On'), default=True)

    if settings.HAS_TAGGING:
        tags    = TagField(_('Tags'))

        def _save_tags(self, *args, **kwargs):
            '''Helper method which makes sure,
               that tags are binded to GeneralPost
               content type.'''
            instance = self.downcast()
            setattr(instance, '_tags_cache', self._tags_cache)
            self._meta.get_field('tags')._save(instance=instance)

        def get_tags(self, *args, **kwargs):
            return Tag.objects.get_for_object(self.downcast())
    else:
        def __init__(self, *args, **kwargs):
            if kwargs.pop('tags', None) is not None:
                logging.getLogger('django_dzenlog').warning(
                    'Tagging is not supported, '
                    'add "tagging" into the INSTALLED_APPS.')
            super(GeneralPost, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def downcast(self):
        return getattr(self, 'generalpost_ptr', self)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-publish_at',)

    def get_edit_url(self):
        return reverse('admin-root',
                        args = ['/'.join((
                            self._meta.app_label,
                            self._meta.module_name,
                            unicode(self.id)))])

    def upcast(self):
        return upcast(self)

    def get_absolute_url(self):
        try:
            obj = self.upcast()
            return reverse('dzenlog-%s-details' % obj._meta.module_name,
                            kwargs=dict(slug=self.slug))
        except NoReverseMatch:
            return reverse('dzenlog-%s-details' % \
                                self.downcast()._meta.module_name,
                            kwargs=dict(slug=self.slug))

    def save(self):
        today = datetime.today()
        published = False

        if self.id:
            prev = GeneralPost.objects.get(pk = self.id)
            published = \
                prev.publish_at is None and self.publish_at is not None
        else:
            published = (self.publish_at is not None)
            self.created_at = today

        self.updated_at = today


        result = super(GeneralPost, self).save()

        if settings.HAS_TAGGING:
            self._save_tags()

        if published:
            signals.published.send(sender = type(self), instance = self)
            signals.published.send(sender = GeneralPost, instance = self)
        return result

