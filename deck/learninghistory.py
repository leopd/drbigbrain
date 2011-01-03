import logging
import random
from deck.learning import SimpleDeckModel
from deck.learning import LearningModelBase
from deck.card import Card



class HistoryModel(SimpleDeckModel):
    """A sophisticated learning model which considers your history of answers.
    Has multiple piles within the deck: unseen, learning, review, solid.
    Cards start in Unseen.
    Learning is for cards that need frequent reinforcement
    Review is for cards that need infrequent reinforcement, but you don't completely know
    Solid is for cards that don't need to be asked about ever again.
    Discard pile is there as well.
    """

    def __init__(self):
        SimpleDeckModel.__init__(self)
        self.model_seq=0
        self.soonest={}

    def supported_actions(self):
        return ['Yes','No','Discard','Kinda']

    def supported_piles(self):
        return ['Unseen','Discard','Solid','Learning','Review']


    def sort_pile_by_soonest(self,pile):
        #re-arrange the pile so the lowest soonest is first
        #print u"before sort: %s" % self
        #print u"soonest: %s" % self.soonest

        # first make a list of tuples of (soonest,card)
        tuplist = []
        for card in self.piles[pile]:
            tuplist.append( ( self.lookup_soonest(card), card ) )
        
        tuplist.sort()

        # now get the cards out of the sorted list and put them in the pile
        self.piles[pile]=[]
        for tup in tuplist:
            self.piles[pile].append( tup[1] )

        #print u"after sort: %s" % self
        #print u"soonest: %s" % self.soonest

        pass


    
    def choose_card(self):
        # update the "clock" so we can pick cards that are destined for later.
        self.seq_tick()

        logging.debug("Choosing card.  model seq up to %s" % self.model_seq)

        card = self.front_of_pile('Learning')
        if (card != None ) and (not self.too_soon(card)):
            logging.debug("from learning pile")
            return card
        logging.debug("Nothing good in learning pile")
        
        card = self.front_of_pile('Review')
        if (card != None ) and (not self.too_soon(card)):
            logging.debug("from review pile")
            return card
        logging.debug("Nothing good in review pile")
        
        card = self.front_of_pile('Unseen')
        if (card != None ):
            logging.debug("from new pile: %s", card)
            return card
        logging.debug("Nothing at all in unseen pile")

        
        card = self.front_of_pile('Learning')
        if (card != None ):
            logging.debug("backup from learning pile")
            return card
        logging.debug("Nothing at all in learning pile")
        
        card = self.front_of_pile('Review')
        if (card != None ):
            logging.debug("backup from review pile")
            return card
        logging.debug("Nothing at all in review pile")
        
        raise OutOfCards("can't find any more to do in deck")


    def choose_many_cards(self,num):
        """Overriding the default method here in the base class
        because I want to trash the cards in between calls
        to choose_card since we don't 'rotate the deck' in this model.
        """

        cards = []
        for i in range(num):
            newcard = self.choose_card()
            cards.append(newcard)

            # Simulate discarding it so that we are sure to 
            # pick a different card the next time around in the loop
            self.move_card_to_pile(newcard,'Discard')

        return cards



    def log_impression(self,impression):
        logging.debug("Logging impression %s" % impression)

        self.seq_tick()
        # updates model_seq - must do this now since this is when the model gets persisted
        #TODO: fix encapsulation of seq_tick.  this is handled in base class.

        card = Card.lookup_card(impression.concept_id)
        next_status = self.get_next_card_status(card,impression.answer)
        logging.debug("Moving card to %s", next_status)
        self.move_card_to_pile(card,next_status)
        self.calculate_soonest(card)
    
        card.log_impression(impression)


    def get_next_card_status(self,card,answer):
        """This is state-machine logic for what pile to put the card into
        based on the answer and where it was
        """
        history = card.history()
        previous_answer = history.previous_answer()
        previous_status = self.which_pile(card) or "Unseen"
        logging.debug("Card was in %s", previous_status)

        if answer == "Discard":
            return 'Discard'

        if answer == "Yes":
            if previous_status == 'Unseen':
                return 'Solid'
            if previous_answer == 'No':
                return 'Learning'
            if previous_answer == 'Kinda':
                return 'Review'
            if previous_answer == 'Yes':
                if previous_status == 'Review':
                    #TODO: consider if they've had problems with it to keep
                    # it in review for a while longer
                    return 'Solid'
                return 'Review'
            # should only get here if previous answer was "discard"
            return 'Review'

        if answer == "No":
            return 'Learning'

        if answer == "Kinda":
            if previous_status == 'Unseen':
                return 'Review'
            if previous_answer == 'Yes':
                return 'Review'
            return 'Learning'

        # shouldn't get here.
        logging.warning("State machine fall-through")
        return None


    # figures out how long we should wait before showing this card again
    def calculate_soonest(self,card):
        status = self.which_pile(card)
        if status == 'Learning':
            #TODO: make this vary with history
            delay = random.uniform(6,12)
        elif status == 'Review':
            #TODO: make this vary with history
            delay = random.uniform(20,40)
        else:
            delay = 100
        self.soonest[card.id] = self.model_seq + delay

        # re-sort this list if it matters
        if (status == 'Learning') or (status == 'Review'):
            self.sort_pile_by_soonest(status)


    def lookup_soonest(self,card,default=None):
        soonest = self.soonest.get(card.id)
        if soonest is None:
            # it's new.  must be fine.
            return default
        return soonest


    # Checks if it's too soon to use a particular card
    def too_soon(self,card):
        soonest = self.soonest.get(card.id)
        if soonest is None:
            # it's new.  must be fine.
            return False

        #print u"Card too soon? %s < %s (%s)" % (self.model_seq, soonest, card)
        return self.model_seq < soonest

    def get_default_new_pile(self):
        """We don't have an 'Active' pile in this model.
        """
        return 'Unseen'
        
    def debug_output_for_card(self,card):
        """ Decorate with soonest
        """
        soonest = self.lookup_soonest(card)
        return u"(%s) [@%s] %s\n" % (card.id, soonest, card)


