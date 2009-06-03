from setuptools import setup, find_packages

setup(
    name = 'django-dzenlog',
    version = __import__('django_dzenlog').__version__,
    description = '''Django Dzenlog is a set of models and templates, which can be '''
                  '''used to create blogs with different kinds media.''',
    long_description = '''
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
    ''',
    keywords = 'django apps blogging',
    license = 'New BSD License',
    author = 'Alexander Artemenko',
    author_email = 'svetlyak.40wt@gmail.com',
    url = 'http://github.com/svetlyak40wt/django-dzenlog/',
    install_requires = [],
    extras_require = {
        'tagging': ['tagging>=0.3-pre'],
    },
    dependency_links = ['http://pypi.aartemenko.com', ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(exclude=['example*']),
    package_data = {
        'templates': ['*.html'],
    },
    include_package_data = True,
    zip_safe = False,
)

