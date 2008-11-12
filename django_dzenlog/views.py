from django.http import Http404
from django.views.generic.list_detail import object_list
from django.contrib.syndication.views import feed as syndication_feed

from tagging.models import Tag, TaggedItem

from models import GeneralPost, published

def get_tags_by_slug(slug):
    return Tag.objects.filter(name__in = slug.split('+'))

def get_tagged(slug, queryset = None, tags = None):
    tags = tags or get_tags_by_slug(slug)

    if queryset is None:
        queryset = GeneralPost.objects.all()

    queryset = published(queryset)

    # Magic starts here.
    # I am mangling with queryset's model
    # attribute to make 'tagging' belive
    # that it is operates on GeneralPost type.
    general_queryset = queryset.all()
    general_queryset.model = GeneralPost

    tagged_queryset = TaggedItem.objects.get_by_model(general_queryset, tags)
    tagged_queryset.model = queryset.model
    # End of magic.
    return tagged_queryset, tags


def bytag(request, slug, queryset = None, template_name = None, extra_context = {}):
    queryset, tags = get_tagged(slug, queryset)

    extra_context_ = extra_context.copy()
    extra_context_['tags'] = tags
    extra_context_['tags_slug'] = slug

    kwargs = {
        'queryset': queryset,
        'extra_context': extra_context_,
    }
    if template_name is not None:
        kwargs['template_name'] = template_name

    return object_list(request, **kwargs)

def post_list(request, **kwargs):
    kwargs['queryset'] = published(kwargs['queryset'])
    return object_list(request, **kwargs)


def feed(request, slug, param = None, feed_dict = None):
    url = slug
    if param is not None:
        url += '/' + param
    return syndication_feed(request, url, feed_dict)
