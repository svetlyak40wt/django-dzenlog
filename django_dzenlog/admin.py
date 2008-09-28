from django.contrib import admin
import settings

class GeneralPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'publish_at']
    if settings.HAS_TAGGING:
        list_display.append('tags')

    prepopulated_fields = {
        'slug': ('title',)
    }

