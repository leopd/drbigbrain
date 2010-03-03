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



    def test_model_creation(self):
	pass


    def test_reset_deck(self):
	pass


    def test_loadsave_model(self):
	"""
	This should test the get_model and save-model methods.
	This requires a mock request.
	"""
	pass


    def test_all_yes_studying(self):
	"""
	Test what the model does when given all Yes answers.
	"""



    def default_lesson(self):
        lesson = Lesson.objects.all()[0]
        return lesson
        

    def setup_model(self,model):
        """Fills the model with a standard lesson set for testing
        """
        model.clear()
        lesson = self.default_lesson()
        model.set_lesson(lesson)


    def try_all_no(self,model,num=100,max_uniq=20):
        """Test that if we always answer 'no' that the deck does not run out after num answers
        """

        self.setup_model(model)
        cnt = 0
	unique_cards = {}
        while( cnt < num ):
            card = model.next_card()
            self.fail_if(card is None)
	    unique_cards[card] = 1
            model.impression(card,'No')
            cnt +=1

	#check that we got a maximum number of unique cards
	num_uniq = len( unique_cards.keys() )
	self.assertTrue( num_unique < max_uniq )


    def repeat_same_answer_expect_unique_set(self,model,cardset,answer):
        """Test that if we always answer the same thing that we don't get the same card twice.
        In fact, we should get each of the cards in cardset exactly once.
        Model should be loaded with cards when we get it.
        """

        self.assertTrue(cardset.count() < 100)
        cnt=0

        while( cardset.count() > 0 ):
            # get a card, and check that we haven't seen it before.

            card = model.next_card()
            try:
                cardset.remove(card)
            except ValueError:
                self.fail("Model chose a repeated card, or one that wasn't in the lesson")

            # mark the card as "yes"
            model.impression(card,'Yes')

            # increment a counter to avoid an infinite loop
            cnt+= 1
            if cnt > 100:
                self.fail("Lesson did not clear after 100 cards.")


    def try_all_discard(self,model):
        """Test that if we always answer 'yes' that we don't get the same card twice.
        """

        self.setup_model(model)
        expected_cards = self.default_lesson().cards()

        self.repeat_same_answer_expect_unique_set(model,expected_cards,'Discard')


    def try_all_yes(self,model):
        """Test that if we always answer 'yes' that we don't get the same card twice.
        """

        self.setup_model(model)
        expected_cards = self.default_lesson().cards()

        self.repeat_same_answer_expect_unique_set(model,expected_cards,'Yes')


    def try_prefetch_identical(self,model,numcards):
	"""Check that when you prefetch twice you get all the same
	cards.
	"""
        p = pickle(model)
	m = unpickle(p)
        prefetch1 = m.get_multipe_cards(numcards)
	m = unpickle(p)
        prefetch2 = m.get_multipe_cards(numcards)
	self.assertEqual(prefetch1,prefetch2)



    def test_simpledeck_model(self):
        model = SimpleDeckModel()
        try_all_yes(model)
        try_all_no(model,200)


    def test_history_model(self):
        model = HistoryModel()
        try_all_yes(model)
        try_all_no(model,200)
        try_all_discard(model)


    def test_default_model(self):
        """Run tests on the default model
        """
        model = get_recommended_model()
        try_all_yes(model)
        try_all_no(model,200)
        try_all_discard(model)


    #TODO: refactor how prefetching works.
    #use an explicit call to the model saying "destructive times-step"
    # or something like that.
    # side-effects of get-multiple are too strong and subtle

