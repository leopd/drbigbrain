from dbbpy.flashcards.models import Lesson

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


class FixtureTest(TestCase):
    """
    Test that the fixtures are reasonable.
    """
    fixtures = ['vocab50.json']

    def test_lessons(self):
	# Test that there are lessons in the db
	lessons = Lesson.objects.all()
	self.failUnless(lessons.count() > 0)
