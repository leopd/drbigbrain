from django.test import TestCase
from flashcards.models import Lesson
from flashcards.models import FlashCardType
from flashcards.models import FlashCard
from flashcards.models import Concept
from flashcards.models import AssetType

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


    def test_card_rendering(self):
	"""Creates FlashCard objects out of the "Read Simplified Chinese"
	card type fixture, and the first few concepts.
	Checks that "pinyin" and "simplified" assets show up in answers.
	"""
	# Get a cardtype from fixtures
	cardtype = FlashCardType.objects.all()[0]
	# confirm it's what we expect
	self.failUnless( cardtype.name.find("Read") >= 0 )
	self.failUnless( cardtype.name.find("Simplified") >= 0 )
	# we're going to look for these asset types in the Q&A
	q_asset_type = AssetType.objects.all()[1]
	self.failUnless( q_asset_type.name.find("simplified") >= 0 )
	a_asset_type = AssetType.objects.get(name='pinyin')


	# Go through 10 concepts and check that they're rendering reasonably
	for concept in Concept.objects.all()[0:10]:
	    card = FlashCard(concept = concept, cardtype = cardtype)

	    html_q = card.html_question()
	    q_asset = concept.asset_set.get(asset_type = q_asset_type).content
	    self.failUnless( html_q.find( q_asset ) >= 0 )
	    #print "Found %s in %s" % (q_asset, html_q)

	    html_a = card.html_answer()
	    a_asset = concept.asset_set.get(asset_type = a_asset_type).content
	    self.failUnless( html_a.find( a_asset ) >= 0 )
	    #print "Found %s in %s" % (a_asset, html_a)

