from django.http import Http404
from django.views.generic.list_detail import object_list

from tagging.models import Tag, TaggedItem

from models import GeneralPost


def bytag(request, slug):
    try:
        tags = Tag.objects.filter(name__in = slug.split('+'))
    except Tag.DoesNotExist:
        raise Http404

    return object_list(
        request,
        queryset = TaggedItem.objects.get_by_model(GeneralPost.objects.published(), tags),
        extra_context = {'tags': tags})
