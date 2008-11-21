django-dzenlog
--------------

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
is to define two models: `TextPost` and `LinkPost`. Each of these
models should be derived from `django_dzenlog.models.GeneralPost`.

Features
========

* Simple way to add new types of posts.
* All post types can be agregated in one feed.
* Separate feed for each post type.
* Example projects, which uses most features of this application.
* Tagging support.
* Custom comments support.

Installation
============

* Place `django_dzenlog` somewhere in the `PYTHONPATH`.
* Add `django_dzenlog` to you `INSTALLED_APPS`.
* Inherit you models from django_dzenlog.models.GeneralPost.
  You can find few examples in the 'example' project.
* Run `./manage.py syncdb` to create database tables.
* Enjoy!

Optionally, you can set these params in the settings.py:

* `DZENLOG_TAGCLOUD_MINCOUNT`, minimum count of tagged objects (default 0).
* `DZENLOG_TAGCLOUD_STEPS`, tag cloud's level count (default 4).
* `DZENLOG_RSS_LENGTH`, maximum entries count in RSS feeds (default 20).

Also, separate RSS feeds for different post types can be added to settings.
For example, you can tell dzenlog, that your feeds are on the feedburner:

    DZENLOG_GENERALPOST_FEED = 'http://feeds.feedburner.com/LazyCrazyCoder'
    DZENLOG_TEXTPOST_FEED = 'http://feeds.feedburner.com/LazyCrazyCoder/text'

If you use some commenting system, than you can define your comment's feeds too:

    DZENLOG_GENERALPOST_ALL_COMMENTS_FEED = \
        'http://feeds.feedburner.com/LazyCrazyCoder/comments'
    DZENLOG_TEXTPOST_ALL_COMMENTS_FEED = \
        'http://feeds.feedburner.com/LazyCrazyCoder/comments/text'

But that does not changes URLs of real feeds, and they will be able at /blog/rss/
and /text/rss/. These settings are affect on HTML generation only.

Templates
=========

In your models you can override these class variables, to set
templates for entry rendering in different sutuations.

Here all templates with their's default values:

    # Render post list
    list_template             = 'django_dzenlog/list.html'
    # Render post with it's details (tags, comments, etc.)
    detail_template           = 'django_dzenlog/detail.html'
    # Render tag cloud (if you has 'tagging' app enabled.)
    tagcloud_template         = 'django_dzenlog/tagcloud.html'
    # Post's body for detailed view.
    body_detail_template      = 'django_dzenlog/body_detail.html'
    # Post's body for list view (for example it can omit full article's text)
    body_list_template        = 'django_dzenlog/body_list.html'
    # Post's title for RSS feed
    feed_title_template       = 'django_dzenlog/feed_title.html'
    # Post's body for RSS feed
    feed_description_template = 'django_dzenlog/feed_description.html'

Also, you can override `django_dzenlog/base.html` to define you own
look and feel. But don't forget to include `django_dzenlog/feeds.html`
to activate automagical feed link generation.

    {% include 'django_dzenlog/feeds.html' %}

Comments handling
=================

TODO: write decription.


Examples
========

To learn, how to use Dzenlog, see example projects in the 'example'
directory. It contains an example application 'blog' with two
models, one for textual blog posts and another -- for links with
descriptions.

TODO
====

* Add caching.
* Add support for django-multilingual in the title and tags.

Any help would be appreciated! Please, send your patches to svetlyak.40wt@gmail.com.
