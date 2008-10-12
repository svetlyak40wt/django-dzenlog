import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

import settings
from pdb import set_trace

if settings.HAS_TAGGING:
    from tagging.fields import TagField
    from tagging.models import Tag


from utils import upcast, virtual


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


    def __unicode__(self):
        return self.title

    def _downcast(self):
        return getattr(self, 'generalpost_ptr', self)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-publish_at',)

    @virtual
    def _get_template(self):
        return 'django_dzenlog/generalpost.html'

    def render(self):
        return render_to_string(
                self._get_template(),
                dict(object=upcast(self), settings=settings))

    def render_feed(self):
        return render_to_string(
                self._get_template(),
                dict(object=upcast(self), settings=settings, for_feed=True))

    @models.permalink
    def get_absolute_url(self):
        return self._get_absolute_url()

    @virtual
    def _get_absolute_url(self):
        return ('dzenlog-post-details', (), dict(slug=self.slug))

    def save(self):
        today = datetime.datetime.today()
        if not self.id:
            self.created_at = today
        self.updated_at = today

        result = super(GeneralPost, self).save()

        if settings.HAS_TAGGING:
            self._save_tags()

        return result

