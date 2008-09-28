from django.db import models
from django.utils.translation import ugettext_lazy as _
import settings

if settings.HAS_TAGGING:
    from tagging.fields import TagField

class GeneralPost(models.Model):
    title       = models.CharField(_('Title'), max_length=100)
    slug        = models.SlugField(_('Slug title'), max_length=100, unique=True)
    created_on  = models.DateTimeField(_('Create date'), blank=True)
    updated_on  = models.DateTimeField(_('Update date'), blank=True)
    publish_on  = models.DateTimeField(_('Publish date'), blank=True, null=True)
    comments_on = models.BooleanField(_('Comments On'), default=True)

    if settings.HAS_TAGGING:
        tags    = TagField()

    def __unicode__(self):
        return self.title
