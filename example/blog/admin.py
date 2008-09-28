from django.contrib import admin
from models import TextPost, LinkPost
from django_dzenlog.admin import GeneralPostAdmin

admin.site.register(TextPost, GeneralPostAdmin)
admin.site.register(LinkPost, GeneralPostAdmin)
