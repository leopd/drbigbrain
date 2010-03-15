import cPickle as pickle
from django.test import TestCase
from flashcards.models import Lesson
from deck.models import Impression
from deck.learninghistory import HistoryModel
from deck.learning import SimpleDeckModel
from deck.learning import RandomLearningModel
from deck.card import Card

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



    def todotest_model_creation(self):
        pass


    def todotest_reset_deck(self):
        pass


    def todotest_loadsave_model(self):
        """
        This should test the get_model and save-model methods.
        This requires a mock request.
        """
        pass




    def default_lesson(self):
        lesson = Lesson.objects.all()[0]
        return lesson
        

    def setup_model(self,model):
        """Fills the model with a standard lesson set for testing
        """
        model.clear()
        lesson = self.default_lesson()
        model.set_active_lesson(lesson.id)


    def simulate_impression(self,model,card,answer):
        impression = Impression()
        impression.concept = card.concept()
        impression.answer = answer
        model.log_impression(impression)

    def try_all_no(self,model,num=100,max_uniq=20):
        """Test that if we always answer 'no' that the deck does not run out after num answers
        """

        self.setup_model(model)
        cnt = 0
        unique_cards = {}
        while( cnt < num ):
            card = model.choose_card()
            self.failIf(card is None)
            unique_cards[card] = 1
            self.simulate_impression(model,card,'No')
            cnt +=1

        #check that we got a maximum number of unique cards
        num_unique = len( unique_cards.keys() )
        self.assertTrue( num_unique < max_uniq )


    def repeat_same_answer_expect_unique_set(self,model,cardset,answer):
        """Test that if we always answer the same thing that we don't get the same card twice.
        In fact, we should get each of the cards in cardset exactly once.
        Model should be loaded with cards when we get it.
        """

        self.assertTrue(len(cardset) < 100)
        cnt=0

        while( len(cardset) > 0 ):
            # get a card, and check that we haven't seen it before.

            card = model.choose_card()
            try:
                cardset.remove(card)
            except ValueError:
                self.fail("Model chose a repeated card, or one that wasn't in the lesson")

            # mark the card as (answer)
            self.simulate_impression(model,card,answer)

            # increment a counter to avoid an infinite loop
            cnt+= 1
            if cnt > 100:
                self.fail("Lesson did not clear after 100 cards.")


    def get_cards_for_lesson(self,lesson,model):
        """This is a mess.  
        """

        cards = []
        for concept in lesson.concepts.all():
            card = Card.lookup_card(concept.id)
            cards.append(card)
            
        return cards



    def try_all_discard(self,model):
        """Test that if we always answer 'yes' that we don't get the same card twice.
        """

        self.setup_model(model)
        expected_cards = self.get_cards_for_lesson(self.default_lesson(),model)

        self.repeat_same_answer_expect_unique_set(model,expected_cards,'Discard')


    def try_all_yes(self,model):
        """Test that if we always answer 'yes' that we don't get the same card twice.
        """

        self.setup_model(model)
        expected_cards = self.get_cards_for_lesson(self.default_lesson(),model)

        self.repeat_same_answer_expect_unique_set(model,expected_cards,'Yes')



    def try_prefetch_identical(self,model,numcards):
        """Check that when you prefetch twice you get all the same
        cards.
        """
        self.setup_model(model)
        p = pickle.dumps(model)
        m = pickle.loads(p)
        prefetch1 = m.choose_many_cards(numcards)
        m = pickle.loads(p)
        prefetch2 = m.choose_many_cards(numcards)
        
        # Check that the lists are identical
        for card1 in prefetch1:
            card2 = prefetch2[0]
            prefetch2 = prefetch2[1:]

            self.assertEqual(card1.json(), card2.json())



    def test_simpledeck_model(self):
        model = SimpleDeckModel()
        self.try_prefetch_identical(model,10)
        self.try_all_yes(model)
        self.try_all_no(model,200)


    def test_history_model(self):
        model = HistoryModel()
        self.try_prefetch_identical(model,10)
        self.try_all_yes(model)
        self.try_all_no(model,200, 15)
        self.try_all_discard(model)


    #TODO: run tests on the "recommended" model


    #TODO: refactor how prefetching works.
    #use an explicit call to the model saying "destructive times-step"
    # or something like that.
    # side-effects of get-multiple are too strong and subtle

