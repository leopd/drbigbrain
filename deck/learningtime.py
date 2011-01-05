import datetime
import logging
import random
import math
from deck.learning import SimpleDeckModel
from deck.learning import LearningModelBase
from deck.learning import OutOfCards
from deck.card import Card


#
# Heuristics
#

# How long should the ERT be after the first time somebody sees one.
DEFAULT_ERT_YES = 15 * 86400
DEFAULT_ERT_NO = 60
DEFAULT_ERT_KINDA = 30 * 60

# ERT will be the exension (below) times the last delay
ERT_EXTENSION_YES = 3.0
ERT_EXTENSION_NO = 0.3
ERT_EXTENSION_KINDA = 0.7

# Interpretion of ERT in terms to actual dela
MINIMUM_ERT_RATIO = 0.8
MAXIMUM_ERT_RATIO = 50.0  # This is the "triage" time


def td_to_seconds(td):
    # built in to python 2.7 and above...
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6




class TimeModel(SimpleDeckModel):
    """A sophisticated learning model which considers your history of answers.
    It uses wall-clock time to decide which cards to show you.
    Piles:
        -Unseen
        -Triaged
        -Learning
        -Discard
    Cards start in Unseen.
    Learning is for cards being learned.
    Triaged is for cards that we think you've forgotten because you went too long.
    Solid is for cards you've never gotten wrong.
    Discard pile is there as well.
    """

    def __init__(self):
        SimpleDeckModel.__init__(self)
        self._metadata={}

    def supported_actions(self):
        return ['Yes','No','Discard','Kinda']

    def supported_piles(self):
        return ['Unseen','Discard','Learning','Triaged']

    def get_default_new_pile(self):
        """We don't have an 'Active' pile in this model.
        """
        return 'Unseen'



    def choose_card(self):
        logging.debug("Choosing a card")

        learning = self.next_ready_card("Learning")
        if learning:
            logging.debug("Choosing from Learning pile: %s" % learning)
            return learning

        card = self.front_of_pile('Triaged')
        if (card != None ):
            logging.debug("Choosing from Triaged pile: %s", card)
            return card

        card = self.front_of_pile('Unseen')
        if (card != None ):
            logging.debug("Choosing from Unseen pile: %s", card)
            return card

        logging.error("We gotta do something better than just throw an exception when we're out of cards.")
        raise OutOfCards("None ready")


    def _add_new_card(self,card,pile):
        history = card.history()
        impr = history.lookup_last_impression()
        if impr:
            ert = self._estimate_ert(card)
            self._set_card_metadata(card,'ert',ert)
            howold = td_to_seconds(datetime.datetime.now() - impr.answered_date)
            if howold > ert * MAXIMUM_ERT_RATIO:
                LearningModelBase._add_new_card(self,card,'Triaged')
            else:
                LearningModelBase._add_new_card(self,card,'Learning')
        else:
            # base class to put it in the default (Unseen) pile
            LearningModelBase._add_new_card(self,card,pile)



    def _estimate_ert(self,card):
        """This new card is being added to the deck.
        Let's go through its history and figure out what its ERT should be.
        """
        # First pull the list of impressions for this card.
        logging.debug(u"Estimating ERT for %s - %s" % (card,card.concept()))
        history = card.history()
        (td_delay, howfarback_last_yes) = history.delay_on_most_recent_yes()
        logging.debug("   Last yes was %s impressions back with a delay of %s" % (howfarback_last_yes,td_delay))
        last_impression = history.lookup_last_impression()
        if td_delay is not None:
            yes_delay = td_to_seconds(td_delay)
        else:
            yes_delay = None
        if howfarback_last_yes is None:
            # They've never gotten this right.
            # TODO: Make this more sophisticated for Kinda
            logging.debug("   Setting to default_ert_no")
            return DEFAULT_ERT_NO 

        if howfarback_last_yes == 0:
            # their last answer was Yes.
            logging.debug("   Last impression was yes")
            if yes_delay is None:
                # Their first and only answer was Yes
                logging.debug("   Setting to default_ert_yes")
                return DEFAULT_ERT_YES
            else:
                logging.debug("   Last answer was YES.  Searching for longest success.")
                longest_delay = history.delay_on_longest_yes()
                logging.debug("   Longest Yes delay was %s" % longest_delay)
                logging.debug("   This Yes delay was %s" % td_delay)
                #TODO: Gotta incorporate how many NOs there are since then!
                ert = td_to_seconds(longest_delay) * ERT_EXTENSION_YES
                logging.debug("   Extending longest to %s" % ert)
                return ert

        # They had a yes in the past, but have screwed up since then.
        logging.debug("   Had a yes, but not most recent.")
        # TODO: Make this better
        if yes_delay is None:
            # Their first answer was Yes, and that was their only yes
            ert = DEFAULT_ERT_YES * (ERT_EXTENSION_NO ** howfarback_last_yes)
            logging.debug("   Only yes was first. Setting ert to %s" % ert)
            return ert
        else:
            if last_impression.answer == 'Kinda':
                # Consider both the longest delay and the most recent.
                longest_delay = td_to_seconds(history.delay_on_longest_yes())
                # geometric mean.
                ert = math.sqrt(yes_delay*longest_delay) * (ERT_EXTENSION_NO ** howfarback_last_yes)
                logging.debug("   Mixed yes and no with recent Kinda. Setting ert to %s" % ert)
            else:
                ert = yes_delay * (ERT_EXTENSION_NO ** howfarback_last_yes)
                logging.debug("   Mixed yes and no. Setting ert to %s" % ert)
            return ert



    def next_ready_card(self,pile):
        """Checks if there's a card ready from this pile.  If so, return it.
        """
        for card in self.piles[pile]:
            howlong = self.how_long_ago(card)
            ert = self._get_card_metadata(card,'ert')
            if not ert:
                logging.warn("Setting ERT to default value for %s in pile %s" % (card,pile))
                ert = DEFAULT_ERT_KINDA
            if not howlong:
                logging.error("Why is %s in %s pile? It has no previous impression." % (card,pile))
                continue
            ert_ratio = howlong / ert
            if ert_ratio < MINIMUM_ERT_RATIO:
                logging.debug("skipping card %s with ERT_RATIO %s and delay %s" % (card, ert_ratio, howlong))
                continue
            if ert_ratio > MAXIMUM_ERT_RATIO:
                self.move_card_to_pile(card,'Triaged')
                #TODO: MAke sure this isn't messing with the for-loop
                continue
            # Passed all checks.  Let's use it.
            logging.debug("Choosing card %s with ERT_RATIO %s and delay %s" % (card, ert_ratio, howlong))
            return card
        return None


    def how_long_ago(self,card):
        """Returns how long it's been since the card's last impression.
        Returns None if it hasn't been seen before.
        """
        history = card.history()
        impr = history.lookup_last_impression()
        if impr:
            now = datetime.datetime.now()
            then = impr.answered_date
            td = now - then
            return td_to_seconds(td)
        else:
            return None

    def get_ert(self,card):
        return self._get_card_metadata(card,'ert')


    def next_exposure_date(self,card):
        history = card.history()
        last_impr = history.lookup_last_impression()
        if not last_impr:
            return None
        last = last_impr.answered_date
        ert = self.get_ert(card)
        if ert is None:
            return None
        next = last + datetime.timedelta(seconds = ert)
        return next
        

    def _metadata_for_card(self,card):
        """Returns all meta-data as a dict
        """
        m = self._metadata.get(card)
        if m:
            return m
        self._metadata[card]={}
        return self._metadata[card]


    def _get_card_metadata(self,card,field):
        """Looks up a piece of metadata about a card
        """
        meta = self._metadata_for_card(card)
        value = meta.get(field)
        logging.debug("Fetching metadata %s as %s for %s"%(field,value,card))
        return value


    def _set_card_metadata(self,card,field,value):
        logging.debug("Setting metadata %s to %s for %s"%(field,value,card))
        meta = self._metadata_for_card(card)
        meta[field]=value
        


    #TODO: Move this into a base class.
    def choose_many_cards(self,num):
        """Overriding the default method here in the base class
        because I want to trash the cards in between calls
        to choose_card since we don't 'rotate the deck' in this model.
        """

        cards = []
        for i in range(num):
            try:
                newcard = self.choose_card()
                cards.append(newcard)
            except OutOfCards:
                logging.info("Couldn't fetch %s cards. Stopping at %s" % (num,i))
                break

            # Simulate discarding it so that we are sure to 
            # pick a different card the next time around in the loop
            self.move_card_to_pile(newcard,'Discard')

        return cards



    #TODO: move to base class
    def log_impression(self,impression):
        logging.debug(u"Logging impression %s" % impression)

        card = Card.lookup_card(impression.concept_id)
        card.log_impression(impression)
        self.seq_tick()

        history = card.history()
        previous_impression = history.lookup_earlier_impression(1)
        # If they don't differ we need to muck with the code.
        if previous_impression:
            current_delay = td_to_seconds(impression.answered_date - previous_impression.answered_date)
        else:
            current_delay = None
        logging.debug(u"Current delay is %s" % current_delay) # This might not work.
        current_answer = impression.answer
        if impression.answer == 'Discard':
            self.move_card_to_pile(card,'Discard')
        else:
            self.evaluate_card(card,current_delay,impression.answer)
            self.move_card_to_pile(card,'Learning')  # We're always learning all these.



    def evaluate_card(self,card,current_delay,current_answer):
        """Adjusts the internal metrics (ERT) to the last response.
        """
        new_ert = None
        old_ert = self._get_card_metadata(card,'ert')
        if current_delay is None:
            # i.e. first time
            if current_answer == 'Yes':
                new_ert = DEFAULT_ERT_YES
            elif current_answer == 'No':
                new_ert = DEFAULT_ERT_NO
            elif current_answer == 'Kinda':
                new_ert = DEFAULT_ERT_KINDA
            else:
                raise NotImplementedError("Unknown answer %s" % current_answer)
        else:
            if current_answer == 'Yes':
                new_ert = current_delay * ERT_EXTENSION_YES
            elif current_answer == 'No':
                # They got it wrong.
                new_ert = current_delay * ERT_EXTENSION_NO
                if old_ert and current_delay > old_ert:
                    # We waited too long.
                    new_ert = old_ert * ERT_EXTENSION_NO
            elif current_answer == 'Kinda':
                new_ert = current_delay * ERT_EXTENSION_KINDA
            else:
                raise NotImplementedError("Unknown answer %s" % current_answer)
        if new_ert:
            self._set_card_metadata(card,'ert',new_ert)
        else:
            logging.error("Somehow we didn't set an ERT in evaluate_card")


