from datetime import datetime, timedelta
from pdb import set_trace

from django.test import TestCase
from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template import Context
from django.template.loader import get_template_from_string

from tagging.models import Tag
from tagging.fields import TagField

from django_dzenlog.models import GeneralPost
from django_dzenlog.settings import HAS_TAGGING


class Parent(models.Model): pass
class Child(Parent): pass
class Child2(Parent): pass


class TestPost(GeneralPost): pass
class TestPost2(GeneralPost): pass

if HAS_TAGGING:
    class Tagging(TestCase):
        def setUp(self):
            (self.author, created) = User.objects.get_or_create(username='tester')

        def testSettingTags(self):
            p = TestPost(author=self.author, title='test', slug='test', tags='one, two, three')
            p.save()

            p2 = GeneralPost.objects.get(id=p.id)
            self.assertEqual('one, two, three', p2.tags)

            tags = Tag.objects.get_for_object(p2)
            self.assertEqual(3, len(tags))

        def testUpdateTags(self):
            p = TestPost(author=self.author, title='test', slug='test', tags='one, two, three')
            p.save()

            tags = p.get_tags()
            self.assertEqual(3, len(tags))

            p.tags = ''
            p.save()

            tags = p.get_tags()
            self.assertEqual(0, len(tags))

            p.tags = 'blah'
            p.save()

            tags = p.get_tags()
            self.assertEqual(1, len(tags))
            self.assertEqual('blah', tags[0].name)

from django.contrib.contenttypes.models import ContentType
from utils import upcast

class Upcast(TestCase):
    def setUp(self):
        Parent.objects.all().delete()

    def testUpcast(self):
        child = Child()
        child.save()

        parent = Parent.objects.get(id=child.parent_ptr_id)

        parent_ct = ContentType.objects.get_for_model(parent)
        parent_ct_upcasted = ContentType.objects.get_for_model(upcast(parent))
        child_ct = ContentType.objects.get_for_model(child)

        self.assertNotEqual(parent_ct, child_ct)
        self.assertEqual(parent_ct_upcasted, child_ct)
        self.assertEqual(upcast(child), child)

    def testUpcastWithMultipleChilds(self):
        child1 = Child()
        child1.save()

        child2 = Child2()
        child2.save()

        self.assertEqual(2, Parent.objects.all().count())

        parent1 = Parent.objects.get(id=child1.parent_ptr_id)
        parent1_ct = ContentType.objects.get_for_model(parent1)
        parent1_ct_upcasted = ContentType.objects.get_for_model(upcast(parent1))

        parent2 = Parent.objects.get(id=child2.parent_ptr_id)
        parent2_ct = ContentType.objects.get_for_model(parent2)
        parent2_ct_upcasted = ContentType.objects.get_for_model(upcast(parent2))

        child1_ct = ContentType.objects.get_for_model(child1)
        child2_ct = ContentType.objects.get_for_model(child2)

        self.assertNotEqual(child1_ct, child2_ct)

        self.assertNotEqual(parent1_ct, child1_ct)
        self.assertEqual(parent1_ct_upcasted, child1_ct)
        self.assertEqual(upcast(parent1), upcast(child1))

        self.assertNotEqual(parent2_ct, child2_ct)
        self.assertEqual(parent2_ct_upcasted, child2_ct)
        self.assertEqual(upcast(parent2), upcast(child2))

class PostsPublicity(TestCase):
    def setUp(self):
        (self.author, created) = User.objects.get_or_create(username='tester')
        TestPost.objects.all().delete()

        TestPost(author=self.author,
                 title='First post',
                 slug='first',
                 tags='one, two',
                 publish_at=datetime.today() - timedelta(0, 60)
                 ).save()
        TestPost(author=self.author,
                 title='Second post',
                 slug='second',
                 tags='one, two'
                 ).save()

    def testInHtml(self):
        response = self.client.get(reverse('dzenlog-generalpost-list'))
        self.assertContains(response, 'First post')
        self.assertNotContains(response, 'Second post')

    def testInRss(self):
        response = self.client.get(reverse('dzenlog-generalpost-feed', kwargs=dict(slug='rss', param='')))
        self.assertContains(response, 'First post')
        self.assertNotContains(response, 'Second post')

    if HAS_TAGGING:
        def testByTag(self):
            response = self.client.get(reverse('dzenlog-generalpost-bytag', kwargs=dict(slug='one')))
            self.assertContains(response, 'First post')
            self.assertNotContains(response, 'Second post')

        def testRssByTag(self):
            TestPost(author=self.author,
                     title='Third post',
                     slug='third',
                     tags='three, four',
                     publish_at=datetime.today() - timedelta(0, 60)
                     ).save()

            response = self.client.get(reverse('dzenlog-generalpost-bytag-feed', kwargs=dict(slug='rss', param='one')))
            self.assertContains(response, 'First post')
            self.assertNotContains(response, 'Second post')
            self.assertNotContains(response, 'Third post')

            response = self.client.get(reverse('dzenlog-generalpost-bytag-feed', kwargs=dict(slug='rss', param='three')))
            self.assertNotContains(response, 'First post')
            self.assertNotContains(response, 'Second post')
            self.assertContains(response, 'Third post')

    else:
        def testHasNoByTag(self):
            self.assertRaises(NoReverseMatch, reverse, 'dzenlog-generalpost-bytag', kwargs=dict(slug='one'))
            self.assertRaises(NoReverseMatch, reverse, 'dzenlog-generalpost-bytag-feed', kwargs=dict(slug='rss', param='one'))

class TemplateTags(TestCase):
    def testCall(self):
        t = get_template_from_string('''{% load dzenlog_tags %}{% call blah minor %}''')
        ctx = Context(dict(blah=lambda x: x, minor='test'))
        self.assertEqual('test', t.render(ctx))

    def testMethod(self):
        class Test:
            def blah(self, x):
                return x

        t = get_template_from_string('''{% load dzenlog_tags %}{% call obj.blah minor %}''')
        ctx = Context(dict(obj=Test(), minor='test'))
        self.assertEqual('test', t.render(ctx))

    def testFunctionNotFound(self):
        from django.template import TemplateSyntaxError
        t = get_template_from_string('''{% load dzenlog_tags %}{% call blah minor %}''')
        ctx = Context(dict(minor='test'))
        self.assertRaises(TemplateSyntaxError, t.render, ctx)

    def testObjectNotFound(self):
        from django.template import TemplateSyntaxError
        t = get_template_from_string('''{% load dzenlog_tags %}{% call obj.blah minor %}''')
        ctx = Context(dict(minor='test'))
        self.assertRaises(TemplateSyntaxError, t.render, ctx)

class Feeds(TestCase):
    def setUp(self):
        (self.author, created) = User.objects.get_or_create(username='tester')
        TestPost.objects.all().delete()

        TestPost(author=self.author,
                 title='First post',
                 slug='first',
                 tags='first-tag, second-tag',
                 publish_at=datetime.today() - timedelta(0, 60)
                 ).save()

    if HAS_TAGGING:
        def testPostCategoriesInRss(self):
            response = self.client.get(reverse('dzenlog-generalpost-feed', kwargs=dict(slug='rss', param='')))
            self.assertContains(response, 'first-tag')
            self.assertContains(response, 'second-tag')

            response = self.client.get(reverse('dzenlog-generalpost-bytag-feed', kwargs=dict(slug='rss', param='first-tag')))
            self.assertContains(response, 'first-tag')
            self.assertContains(response, 'second-tag')

        def testRequestedCategoriesInRss(self):
            TestPost(author=self.author,
                     title='Second post',
                     slug='second',
                     tags='another-tag',
                     ).save()

            tags = ['first-tag', 'another-tag']
            response = self.client.get(reverse('dzenlog-generalpost-bytag-feed', kwargs=dict(slug='rss', param='+'.join(tags))))
            for tag in tags:
                self.assertContains(response, tag)

if HAS_TAGGING:
    class ByTags(TestCase):
        def setUp(self):
            (self.author, created) = User.objects.get_or_create(username='tester')
            TestPost.objects.all().delete()

            TestPost(author=self.author,
                     title='First post',
                     slug='first',
                     tags='one, two',
                     publish_at=datetime.today() - timedelta(0, 60)
                     ).save()

            TestPost2(author=self.author,
                     title='Second post',
                     slug='second',
                     tags='three, four',
                     publish_at=datetime.today() - timedelta(0, 60)
                     ).save()

        def testPostCategoriesInRss(self):
            response = self.client.get(reverse('dzenlog-generalpost-tags'))
            for tag in ['one', 'two', 'three', 'four']:
                self.assertContains(response, tag)


class URLConf(TestCase):
    def testRaiseExceptionOnUnknownModel(self):
        from urls import create_patterns
        self.assertRaises(Exception, create_patterns, 'blah.minor')

class PublishedSignal(TestCase):
    def __init__(self, *args):
        (self.author, created) = User.objects.get_or_create(username='tester')
        self.sended = False

        def receiver(instance, sender, signal):
            self.assertEqual(TestPost, sender)
            self.sended = True

        from signals import published
        published.connect(receiver, sender = TestPost, weak = False)
        super(PublishedSignal, self).__init__(*args)

    def setUp(self):
        self.sended = False

    def testNotSendIfNoDate(self):
        TestPost(author=self.author,
                 title='Test post',
                 slug='first',
                 publish_at=None,
                 ).save()
        self.assertEqual(False, self.sended)

    def testSendIfDate(self):
        TestPost(author=self.author,
                 title='Test post',
                 slug='first',
                 publish_at=datetime.today(),
                 ).save()
        self.assertEqual(True, self.sended)

    def testNotSendOnRemoveFromPublication(self):
        post = TestPost(author=self.author,
                 title='Test post',
                 slug='first',
                 publish_at=datetime.today(),
                 )
        post.save()

        self.assertEqual(True, self.sended)
        self.sended = False

        post.publish_at = None
        post.save()
        self.assertEqual(False, self.sended)

    def testSendOnPublication(self):
        post = TestPost(author=self.author,
                 title='Test post',
                 slug='first',
                 publish_at=None,
                 )
        post.save()

        self.assertEqual(False, self.sended)

        post.publish_at = datetime.today()
        post.save()
        self.assertEqual(True, self.sended)
