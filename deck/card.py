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

	Card.cards_by_id[concept.id] = self


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
    must be pickleable, which means no django objects
    """

    def __init__(self,id):
        self.id = id

        # TODO: Look up the actual previous answer
        self.cachelast= None


    def no_count(self):
        raise NotImplmentedError()


    def previous_answer(self):
        return self.cachelast


    def log_impression(self,impression):
        self.cachelast = impression.answer

