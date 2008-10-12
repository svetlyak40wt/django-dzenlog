from datetime import datetime
from pdb import set_trace

from django.test import TestCase
from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from tagging.models import Tag
from tagging.fields import TagField
from django_dzenlog.models import GeneralPost


class Parent(models.Model): pass
class Child(Parent): pass
class Child2(Parent): pass


class TestPost(GeneralPost): pass

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
                 publish_at=datetime.today()
                 ).save()
        TestPost(author=self.author,
                 title='Second post',
                 slug='second',
                 tags='one, two'
                 ).save()

    def testInHtml(self):
        response = self.client.get(reverse('dzenlog-post-list'))
        self.assertContains(response, 'First post')
        self.assertNotContains(response, 'Second post')

    def testInRss(self):
        response = self.client.get(reverse('dzenlog-feeds', kwargs=dict(url='all')))
        self.assertContains(response, 'First post')
        self.assertNotContains(response, 'Second post')

    def testByTag(self):
        response = self.client.get(reverse('dzenlog-post-bytag', kwargs=dict(slug='one')))
        self.assertContains(response, 'First post')
        self.assertNotContains(response, 'Second post')

