import logging
import random
from django.shortcuts import get_object_or_404
from flashcards.models import Concept
from flashcards.models import Lesson
from deck.models import Impression
from deck.card import Card



class LearningModelBase():
    """base class for learning models
    these must be pickleable
    """


    def __init__(self):
        # cards is a hashtable of lists of Card objects
        self.piles={}
        for pile in self.supported_piles():
            #print "creating pile %s" % pile
            self.piles[pile] = []

        # a string to describe the lessons contained
        self.description=""

        # Number of cards seen by the user
        self.model_seq = 0


    def clear(self):
        """Resets the deck to its initial state.
        """
        self.__init__()


    def get_sequence(self):
        return self.model_seq


    def get_default_new_pile(self):
        """Which pile do new cards go into?
        """
        return 'Active'


    def add_new_cards(self, describe_new_cards, card_id_list, pile=None):
        """Add a whole list of cards to the pile.
        Defaults to the get_default_new_pile() pile.
        Also requires a string describing the new cards.
        """

        # add to the description if there is one
        if self.description != "":
            self.description += ", "
            self.description += describe_new_cards
        else:
            self.description = describe_new_cards

        # figure out which pile to put them in
        if pile is None:
            pile = self.get_default_new_pile()

        # put them into the pile
        for id in card_id_list:
            card = Card.lookup_card(id)
            self.move_card_to_pile(card,pile)

        
    def set_active_lesson(self,lesson_id):
        """given a lesson id, it stores the id's of all the concepts in that lesson
        in the 'default_new' card pile
        """
        lesson = get_object_or_404(Lesson, pk=lesson_id)

        id_list=[]
        #TODO: Replace this with proper sequences from LessonSequence table
        for concept in lesson.concepts.all():
            id_list.append(concept.id)
        
        self.add_new_cards(lesson.name, id_list)


    def supported_piles(self):
        """returns a list of the kinds of piles this model understands
        """
        return ['Active']
    
    def supported_actions(self):
        """Returns a list of the kinds of actions this model understands
           these are the buttons that will be displayed in the study ui
        """
        return ['Next']
    


    def choose_card(self):
        """Returns a Card which should be the next card displayed
        to the user.
        This method is required.  subclasses must implement this.

        Note that the view's behavior is not to save any changes to the 
        model object that result from this.  This can be useful
        when implementing choose_many_cards, because the model can
        just pretend to discard each of the cards that it presents to the
        user to be able to pick the next one.
        """
        raise NotImplementedError()
    

    def choose_many_cards(self,num):
        """Returns a list of the next NUM cards that should be shown to the user.
        Default implementation just calls choose_card multiple times,
        assuming it will get a sensibly different answer each time.
        """

        cards = []
        for i in range(num):
            cards.append(self.choose_card())

        return cards



    def choose_concept(self):
        """Deprecated
        Returns a Concept object for the user to study.
        """

        card = self.choose_card()
        return card.concept()


    def seq_tick(self):
        """Updates the internal timer (model_seq)
        """
        self.model_seq += 1;


    def log_impression(self,impression):
        """Records the fact that the user looked at a card.
        Updates the model based on their answer.
        """
        # basic thing that needs to happen is to increment the model_seq
        self.seq_tick()


    def __unicode__(self):
        """Outputs a debug string with all the piles
        """

        str = u"%s (seq=%s):\n" % (self.__class__, self.model_seq)
        str += u"(%s)\n" % self.description
        for pile in self.supported_piles():
            str += u"%s pile: " % pile
            if self.piles.get(pile) is None:
                str += u"missing\n"
            else:
                str += u"{\n"
                place=0
                for card in self.piles[pile]:
                    place += 1
                    str += u"    %s. %s" % (place, self.debug_output_for_card(card) )
                str += u"}\n"
        return str
        

    def debug_output_for_card(self,card):
        """Outputs a short (one-line) debug string for the card
        Allows sub-classes to decorate the output.
        """
        return u"(%s) %s\n" % (card.id, card)


    # returns a list of cards in the given pile
    def cards_in_pile(self, pile):
        return self.piles[pile]

    def remove_card_from_pile(self,id,pile):
        if pile is None:
            return
        try:
            self.piles[pile].remove(id)
        except ValueError:
            #print "Couldn't find %s in %s list" % (id, pile)
            pass

    # defaults to back of pile
    def move_card_to_pile(self,card,pile,where=-1):
        self.remove_card_from_pile(card, self.which_pile(card) )
        if where < 0:
            self.piles[pile].append(card)
        else:
            self.piles[pile].insert(where,card)



    def front_of_pile(self,pile):
        if len(self.piles[pile]) == 0:
            return None
        return self.piles[pile][0]

    def which_pile(self,card):
        #TODO: this is slow. catching lots of exceptions make it faster.
        for pile in self.supported_piles():
            try:
                self.piles[pile].index(card)
                return pile
            except ValueError:
                pass
        return None    
        


class RandomLearningModel(LearningModelBase):
    """this just picks a random card from the deck, with no ideas of state
    """

    def choose_card(self):
        num = len(self.piles['Active'])
        which = random.randint(0,num-1)

        card = self.piles['Active'][which]
        return card


class SimpleDeckModel(LearningModelBase):
    """Just goes through the cards in order.
    """

    def choose_card(self):
        # Just choose the front card from the Active pile
        card = self.piles['Active'][0]

        # rotate the deck
        # This supports choose_many_cards, but doesn't actually ensure rotation.
        self.move_card_to_pile(card,'Active')
        #self.piles['Active'] = self.piles['Active'][1:]
        #self.piles['Active'].append(card)

        return card

    def log_impression(self,impression):
        LearningModelBase.log_impression(self,impression)

        # here we need to actually rotate the card to the back.
        card = Card.lookup_card(impression.concept_id)
        self.move_card_to_pile(card,'Active')

        

class BetterDeckModel(SimpleDeckModel):
    """A reasonably useful deck model.
    If you get a card right, put it at the back of the deck.
    If you get a card wrong, put it fairly close to the front
    """

    def supported_actions(self):
        return ['Yes','No','Discard']

    def supported_piles(self):
        return ['Active','Discard']
    
    # where to put the card if the user gets it wrong
    def how_far_back_when_wrong(self):
        return int(random.uniform(3,7))
        
    def log_impression(self,impression):
        LearningModelBase.log_impression(self,impression)

        #print u"better decklogging %s" % impression
        card = Card.lookup_card(impression.concept_id)

        # if they got it right, do nothing
        if impression.answer == "Yes":
            #TODO: if impression time was long, move it up some
            return

        if impression.answer == "Discard":
            self.move_card_to_pile(card,'Discard')
            return
            
        if impression.answer == "No":
            # if they got it wrong, move that card near the front of the deck
            self.move_card_to_pile(card,'Active', self.how_far_back_when_wrong())

        #print u"now list is %s" % self.piles['Active']

