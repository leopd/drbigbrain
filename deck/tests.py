from django.test import TestCase
from dbbpy.flashcards.models import Lesson

class SimpleTest(TestCase):
    fixtures = ['vocab50.json']
    
    def test_fixture_data(self):
	"""
	Check that the data loaded in the fixtures is structurally reasonable
	"""

	# Test that there are multiple lessons in the db
	lessons = Lesson.objects.all()
	self.failUnless(lessons.count() >= 1)
	
	# Look for a minimum number of concepts
	lesson = lessons[0]
	self.failUnless(lesson.concepts.count() > 5)


