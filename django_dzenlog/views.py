from django.http import Http404
from django.views.generic.list_detail import object_list

from tagging.models import Tag, TaggedItem

from models import GeneralPost, published


def bytag(request, slug, queryset = None, template_name = None, extra_context = {}):
    try:
        tags = Tag.objects.filter(name__in = slug.split('+'))
    except Tag.DoesNotExist:
        raise Http404

    if queryset is None:
        queryset = published(GeneralPost.objects.all())

    extra_context_ = extra_context.copy()
    extra_context_['tags'] = tags

    # Magic starts here.
    # I am mangling with queryset's model
    # attribute to make 'tagging' belive
    # that it is operates on GeneralPost type.
    general_queryset = queryset.all()
    general_queryset.model = GeneralPost

    tagged_queryset = TaggedItem.objects.get_by_model(general_queryset, tags)
    tagged_queryset.model = queryset.model
    # End of magic.

    kwargs = {
        'queryset': tagged_queryset,
        'extra_context': extra_context_,
    }
    if template_name is not None:
        kwargs['template_name'] = template_name

    return object_list(request, **kwargs)
