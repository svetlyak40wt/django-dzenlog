Description
===========

Django Dzenlog is a set of models and templates, which can be
used to create blogs with different kinds media.

Dzenlog relies on new django's feature -- model inheritance,
so you can derive you own models from dzenlog's models and
add an actual information.

This is very effective way of the code reuse, because dzenlog
will take care about all publishing options, and all what you
need is to describe details, specific to you particular blog.

For example, for can create a blog with two post types: textual
posts and links to internet resources. In that case, all you need
is to define two models: TextPost and LinkPost. Each of these
models should be derived from django_dzenlog.models.GeneralPost.

To learn, how to use Dzenlog, see example projects in the 'example'
directory. It contains an example application 'blog' with two
models, one for textual blog posts and another -- for links with
descriptions.
