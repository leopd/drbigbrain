from django.test import TestCase
from dbbpy.flashcards.models import Lesson

class FixtureTest(TestCase):
    """
    Test that the fixtures are reasonable.

    Note that the fixtures have their unicode stripped out b/c
    of django bugs -- it can't roundtrip through dumpdata, fixtures=
    properly with unicode data. (loaddata works, but not fixtures=)
    """
    fixtures = ['vocab50.json']


    def test_basic_data(self):
	"""
	Check that the data loaded in the fixtures is structurally reasonable
	"""

	# Test that there are multiple lessons in the db
	lessons = Lesson.objects.all()
	self.failUnless(lessons.count() >= 1)
	
	# Look for a minimum number of concepts
	lesson = lessons[0]
	self.failUnless(lesson.concepts.count() > 5)

	# Look inside the concept
	concept = lesson.concepts.all()[0]
	assets = concept.asset_set.all()
	self.failUnless(assets.count() >= 2)

