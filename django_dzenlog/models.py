import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
import settings

if settings.HAS_TAGGING:
    from tagging.fields import TagField

class GeneralPost(models.Model):
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

    def save(self):
        if not self.id:
            self.created_at = datetime.datetime.today()
        self.updated_at = datetime.datetime.today()
        return super(GeneralPost, self).save()

