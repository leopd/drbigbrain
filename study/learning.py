import random
from django.shortcuts import get_object_or_404
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson



# base class for learning models
# these must be pickleable
class LearningModelBase():

    # given a lesson id, it stores the id's of all the concepts in that lesson
    # in a list called active_concepts
    def set_active_lesson(self,lesson_id):
	print "init %s!" % self
	lesson = get_object_or_404(Lesson, pk=lesson_id)
	self.active_concepts = []
	for concept in lesson.concepts.all():
	    self.active_concepts.append(concept.id)
	    

    def choose_card():
	raise NotImplementedError()
    


# this just picks a random card from the deck, with no concept of state
# (beyond the 
class RandomLearningModel(LearningModelBase):

    def choose_card(self):
	print "choose card %s!" % self
	num = len(self.active_concepts)
	which = random.randint(0,num-1)

	concept_id = self.active_concepts[which]
	concept = get_object_or_404(Concept, pk=concept_id)
	return concept


