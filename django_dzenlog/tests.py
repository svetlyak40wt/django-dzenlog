import unittest
from pdb import set_trace

from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import User

from tagging.models import Tag
from django_dzenlog.models import GeneralPost


class Parent(models.Model): pass
class Child(Parent): pass
class Child2(Parent): pass
test_signal = Signal(providing_args=["instance"])


class SignalsAndInheritance(unittest.TestCase):
    def testPropagateToParent(self):
        receiver1 = lambda signal, sender: True

        test_signal.connect(receiver1, Parent, True)

        responses = dict(test_signal.send(sender=Child))
        self.assertEqual(1, len(responses))
        self.assertEqual(True, responses[receiver1])

    def testNotPropagateToChild(self):
        receiver1 = lambda signal, sender: True

        test_signal.connect(receiver1, Child, True)

        responses = dict(test_signal.send(sender=Parent))
        self.assertEqual(0, len(responses))


class TestPost(GeneralPost): pass

class Tagging(unittest.TestCase):
    def setUp(self):
        (self.author, created) = User.objects.get_or_create(username='tester')
#        self.author.save()

    def tearDown(self):
        User.objects.all().delete()

    def testSettingTags(self):
        p = TestPost(author=self.author, title='test', slug='test', tags='one, two, three')
        p.save()

        tags = Tag.objects.get_for_object(p)
        self.assertEqual(3, len(tags))

    def testUpdateTags(self):
        p = TestPost(author=self.author, title='test', slug='test', tags='one, two, three')
        p.save()

        p.tags = ''
        p.save()

        tags = Tag.objects.get_for_object(p)
        self.assertEqual(0, len(tags))

        p.tags = 'blah'
        p.save()

        tags = Tag.objects.get_for_object(p)
        self.assertEqual(1, len(tags))

from django.contrib.contenttypes.models import ContentType
from utils import upcast

class Upcast(unittest.TestCase):
    def setUp(self):
        Parent.objects.all().delete()

    def testInheritance(self):
        child = Child()
        child.save()

        parent = Parent.objects.get(id=child.parent_ptr_id)

        parent_ct = ContentType.objects.get_for_model(parent)
        parent_ct_upcasted = ContentType.objects.get_for_model(upcast(parent))
        child_ct = ContentType.objects.get_for_model(child)

        self.assertNotEqual(parent_ct, child_ct)
        self.assertEqual(parent_ct_upcasted, child_ct)
        self.assertEqual(upcast(child), child)

    def testInheritanceWithMultipleChilds(self):
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

