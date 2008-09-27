from django.db import models

class GeneralPost(models.Model):
    title = models.CharField('Title', max_length=100)
    publish_on = models.DateTimeField('Date', blank=True, null=True)

    def __unicode__(self):
        return 'GeneralPost: %s' % self.title
