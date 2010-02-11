import random
from django.shortcuts import get_object_or_404
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.study.models import Impression



# base class for learning models
# these must be pickleable
class LearningModelBase():

    # given a lesson id, it stores the id's of all the concepts in that lesson
    # in a list called active_concepts
    def set_active_lesson(self,lesson_id):
	lesson = get_object_or_404(Lesson, pk=lesson_id)
	self.active_concepts = []
	for concept in lesson.concepts.all():
	    self.active_concepts.append(concept.id)

	#TODO: Replace this with proper sequences from LessonSequence table
	self.active_concepts.reverse()
	    

    # this method is required
    def choose_card(self):
	raise NotImplementedError()
    

    def log_impression(self,impression):
	# simple models might not use this fact, so they don't need
	# to override this method.
	#print "default logimpression does nothing"
	pass

    def __unicode__(self):
	str = u"%s: {\n" % self.__class__
	place=0
	for id in self.active_concepts:
	    concept = get_object_or_404(Concept, pk=id)
	    place += 1
	    str += u"%s) %s\n" % (place, concept)
	str += "}"
	return str

# this just picks a random card from the deck, with no concept of state
# (beyond the 
class RandomLearningModel(LearningModelBase):

    def choose_card(self):
	num = len(self.active_concepts)
	which = random.randint(0,num-1)

	concept_id = self.active_concepts[which]
	concept = get_object_or_404(Concept, pk=concept_id)
	return concept


# Just goes through the cards in order.
class SimpleDeckModel(LearningModelBase):

    def choose_card(self):
	concept_id = self.active_concepts[0]
	concept = get_object_or_404(Concept, pk=concept_id)

	# rotate the deck
	self.active_concepts = self.active_concepts[1:]
	self.active_concepts.append(concept_id)

	return concept


# If you get a card right, put it at the back of the deck.
# If you get a card wrong, put it fairly close to the front
class BetterDeckModel(SimpleDeckModel):

    # where to put the card if the user gets it wrong
    HOW_FAR_BACK_WHEN_WRONG=5

    def log_impression(self,impression):
	#print u"better decklogging %s" % impression
	# if they got it right, do nothing
	if impression.answer == "yes":
	    return

	# if they got it wrong, move that card near the front of the deck
	try:
	    self.active_concepts.remove(impression.concept_id)
	except ValueError:
	    #print "Couldn't find %s in active list" % impression.concept_id
	    pass
	self.active_concepts.insert(self.HOW_FAR_BACK_WHEN_WRONG,impression.concept_id)

	#print u"now list is %s" % self.active_concepts

