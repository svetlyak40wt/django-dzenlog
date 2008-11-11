import logging
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, NoReverseMatch

import settings
from pdb import set_trace

if settings.HAS_TAGGING:
    from tagging.fields import TagField
    from tagging.models import Tag


from utils import upcast, virtual

def published(queryset):
    return queryset.filter(publish_at__lte=datetime.now())

class GeneralPost(models.Model):
    author      = models.ForeignKey(User)
    title       = models.CharField(_('Title'), max_length=100)
    slug        = models.SlugField(_('Slug title'), max_length=100, unique=True)
    created_at  = models.DateTimeField(_('Create date'), blank=True, editable=False)
    updated_at  = models.DateTimeField(_('Update date'), blank=True, editable=False)
    publish_at  = models.DateTimeField(_('Publish date'), blank=True, null=True)
    comments_on = models.BooleanField(_('Comments On'), default=True)

    if settings.HAS_TAGGING:
        tags    = TagField()

        def _save_tags(self, *args, **kwargs):
            instance = self._downcast()
            setattr(instance, '_tags_cache', self._tags_cache)
            self._meta.get_field('tags')._save(instance=instance)

        def get_tags(self, *args, **kwargs):
            return Tag.objects.get_for_object(self._downcast())
    else:
        def __init__(self, *args, **kwargs):
            if kwargs.pop('tags', None) is not None:
                logging.getLogger('django_dzenlog').warning('Tagging is not supported, add "tagging" into the INSTALLED_APPS.')
            super(GeneralPost, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def _downcast(self):
        return getattr(self, 'generalpost_ptr', self)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-publish_at',)

    def get_edit_url(self):
        return reverse('admin-root', args = ['/'.join((self._meta.app_label, self._meta.module_name, unicode(self.id)))])

    @virtual
    def _get_template(self):
        return 'django_dzenlog/generalpost.html'

    def upcast(self):
        return upcast(self)

    def render(self, **kwargs):
        return render_to_string(
                self._get_template(),
                dict(object=self.upcast(), settings=settings, **kwargs))

    def render_feed(self, **kwargs):
        return render_to_string(
                self._get_template(),
                dict(object=self.upcast(), settings=settings, for_feed=True, **kwargs))

    def get_absolute_url(self):
        try:
            obj = self.upcast()
            return reverse('dzenlog-%s-details' % obj._meta.module_name, kwargs=dict(slug=self.slug))
        except NoReverseMatch:
            return reverse('dzenlog-%s-details' % self._meta.module_name, kwargs=dict(slug=self.slug))

    def save(self):
        today = datetime.today()
        if not self.id:
            self.created_at = today
        self.updated_at = today

        result = super(GeneralPost, self).save()

        if settings.HAS_TAGGING:
            self._save_tags()

        return result

