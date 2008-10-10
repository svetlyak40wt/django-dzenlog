import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

import settings
from pdb import set_trace

if settings.HAS_TAGGING:
    from tagging.fields import TagField


from django.db.models.query import CollectedObjects

def virtual(func):
    '''Find a child object and call method against it
       instead os original 'func'.

       Apply this decorator to any method of the base
       class.
    '''

    def wrap(self, *args, **kwargs):
        if getattr(self, '_child_object', None) is None:
            sub_objects = CollectedObjects()
            self._collect_sub_objects(sub_objects)
            setattr(self,
                    '_child_object',
                    sub_objects.items()[0][1].values()[0])

        child_method = getattr(self._child_object, func.__name__)
        if getattr(child_method, '_is_virtual_wrap', False):
            return func(self, *args, **kwargs)
        return child_method(*args, **kwargs)
    wrap.__doc__  = func.__doc__
    wrap.__name__ = func.__name__
    setattr(wrap, '_is_virtual_wrap', True)
    return wrap

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

    def __unicode__(self):
        return self.title

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
                dict(object=self, settings=settings))

    def render_feed(self):
        return render_to_string(
                self._get_template(),
                dict(object=self, settings=settings, for_feed=True))

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
        return super(GeneralPost, self).save()

