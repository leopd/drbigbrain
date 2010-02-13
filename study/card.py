from django.shortcuts import get_object_or_404
from dbbpy.flashcards.models import Concept
from dbbpy.study.models import Impression


# must be pickleable, which means no django objects
# note this is an instance of a card being studied,
# not a generic data type.  
# the difference is that it's specific to a user.
#TODO: use this more completely in study/views.py
class Card():

    def __init__(self,concept):
	self.id = concept.id
	self._history = History(self.id)


    def summary(self):
	raise NotImplmentedError()


    def question(self):
	raise NotImplmentedError()


    def answer(self):
	raise NotImplmentedError()


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

# represents the study history for a card
# must be pickleable, which means no django objects
class History():

    def __init__(self,id):
	self.id = id

	# TODO: Look up the actual previous answer
	self.cachelast= None

	print "TODO: Look up the actual previous answer"


    def no_count(self):
	print "not calculating no-count properly"
	return 0;


    def previous_answer(self):
	return self.cachelast


    def log_impression(self,impression):
	self.cachelast = impression.answer

