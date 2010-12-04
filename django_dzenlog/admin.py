from django.contrib import admin
import settings

class GeneralPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'publish_at']
    if settings.HAS_TAGGING:
        list_display.append('tags')

    prepopulated_fields = {
        'slug': ('title',)
    }

    def get_form(self, request, *args, **kwargs):
        form = super(GeneralPostAdmin, self).get_form(request, *args, **kwargs)
        form.base_fields['author'].initial = request.user
        return form
