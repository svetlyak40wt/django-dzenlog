from django.utils.translation import ugettext_lazy as _
from south.db import db
from django.db import models
from django_dzenlog.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[])
        
        # Model 'GeneralPost'
        db.create_table('django_dzenlog_generalpost', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(User)),
            ('title', models.CharField(_('Title'), max_length=100)),
            ('slug', models.SlugField(_('Slug title'), max_length=100, unique=True)),
            ('created_at', models.DateTimeField(_('Create date'), blank=True, editable=False)),
            ('updated_at', models.DateTimeField(_('Update date'), blank=True, editable=False)),
            ('publish_at', models.DateTimeField(_('Publish date'), blank=True, null=True)),
            ('comments_on', models.BooleanField(_('Comments On'), default=True)),
            ('tags', TagField()),
        ))
        
        db.send_create_signal('django_dzenlog', ['GeneralPost'])
    
    def backwards(self):
        db.delete_table('django_dzenlog_generalpost')
        
