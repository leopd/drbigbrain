from django.shortcuts import get_object_or_404
from flashcards.models import Concept
from deck.models import Impression


class Card():
    """Abstraction between Concept model and what the user actually studies.
    note this is an instance of a card being studied,
    not a generic data type.  
    the difference is that it's specific to a user.
    use this more completely in study/views.py

    This should support things like a rosetta-style card.
    """


    # methods to create a singleton per id
    cards_by_id={}

    @staticmethod
    def by_id(id):
        """find the card by its id
        """
        card = Card.cards_by_id.get(id)
        if card:
            return card

        # otherwise create a new Card
        concept = get_object_or_404(Concept, pk=id)
        return Card(concept)

    @staticmethod
    def lookup_card(id):
        return Card.by_id(id)

    


    def __init__(self,concept):
        self.id = concept.id
        self._history = History(self.id)

        # Cache this instance as a singleton
        Card.cards_by_id[concept.id] = self

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return other.id == self.id


    def __hash__(self):
        return hash(self.id)


    def __str__(self):
        return "Card #%s" % self.id


    def summary(self):
        raise NotImplmentedError()


    def question(self):
        q = self.concept().asset_set.get(asset_type=2).content
        return q


    def answer(self):
        c = self.concept()
        a = u"<i>%s</i><br/>%s" % (
            c.asset_set.get(asset_type=3).content,
            c.asset_set.get(asset_type=4).content
            )
        return a


    def json(self):
        """Returns a python object that can be rendered as json
        """

        q = self.question()
        a = self.answer()
        data = { 
            "question": q, 
            "answer": a, 
            "id": self.id,
            "summary": unicode(self.concept()),
            }
        return data


    def history(self):
        return self._history

    def concept(self):
        return get_object_or_404(Concept, pk=self.id)


    # return a structure that can be rendered to json
    def jsonable(self):
        raise NotImplmentedError()


    def log_impression(self,impression):
        self._history.log_impression(impression)


    def __unicode__(self):
        return unicode(self.concept())

class History():
    """Helper for Card that keeps track of a user's history for the card.
    represents the study history for a card
    must be pickleable.
    """

    def __init__(self,concept_id):
        self._concept_id = concept_id

        # Used to get away with not actually looking up the previous impression
        #self.__last_impression= None
        self.__last_impression = self.lookup_last_impression()

    def lookup_last_impression(self):
        return self.lookup_earlier_impression(0)

    def lookup_earlier_impression(self,howfar_back):
        concept = Concept.objects.get(pk=self._concept_id)
        all_impressions = Impression.objects.filter(concept = concept).order_by('-answered_date')
        if len(all_impressions) > howfar_back:
            return all_impressions[howfar_back]
        else:
            return None

    def delay_on_most_recent_yes(self):
        """Specialized method for ERT estimation.
        It goes back to the most recent "yes" answer
        and figures out how long the exposure delay was for that answer.
        Returns a tuple of (delay_as_timedelta,howfarback).
        If there are no Yes answers, then it returns (None,None)
        If there is only one Yes and it's the first then you get (None, howfarback)
        howfarback is 0-based.  If the most recent is a yes you get a 0.
        """
        concept = Concept.objects.get(pk=self._concept_id)
        all_impressions = Impression.objects.filter(concept = concept).order_by('-answered_date')
        last_yes = None
        howfarback = -1
        for impr in all_impressions.all():
            if last_yes:
                td = last_yes.answered_date - impr.answered_date
                return (td, howfarback)
            else:
                if impr.answer == 'Yes':
                    last_yes = impr
            howfarback += 1

        if last_yes:
            # The only yes is the first answer
            return (None, howfarback)

        # No yes's
        return (None, None)

    
            



    def no_count(self):
        raise NotImplmentedError()


    def previous_answer(self):
        if self.__last_impression:
            return self.__last_impression.answer
        return None


    def log_impression(self,impression):
        self.__last_impression = impression

