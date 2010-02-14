import random
from django.shortcuts import get_object_or_404
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.study.models import Impression
from dbbpy.study.card import Card



# base class for learning models
# these must be pickleable
class LearningModelBase():

    def __init__(self):
	# cards is a hashtable of lists of Card objects
	self.piles={}
	for pile in self.supported_piles():
	    print "creating pile %s" % pile
	    self.piles[pile] = []

	# this provides a way to look up the card objects 
	self.cards_by_id={}

    # given a lesson id, it stores the id's of all the concepts in that lesson
    # in the "Active" card pile
    def set_active_lesson(self,lesson_id):
	lesson = get_object_or_404(Lesson, pk=lesson_id)

	# reset Active
	self.piles['Active'] = []

	for concept in lesson.concepts.all():
	    card = Card(concept)
	    self.move_card_to_pile(card,'Active')
	    #self.piles['Active'].append(card)

	#TODO: Replace this with proper sequences from LessonSequence table
	#self.piles['Active'].reverse()

    # returns a list of the kinds of piles this model understands
    def supported_piles(self):
	return ['Active']
    
    # returns a list of the kinds of actions this model understands
    # these are the buttons that will be displayed in the study ui
    def supported_actions(self):
	return ['Next']
    


    # this method is required.  subclasses must implement this.
    def choose_card(self):
	raise NotImplementedError()
    

    def choose_concept(self):
	card = self.choose_card()
	return card.concept()

    def log_impression(self,impression):
	# simple models might not use this fact, so they don't need
	# to override this method.
	#print "default logimpression does nothing"
	pass

    def __unicode__(self):
	str = u"%s:\n" % self.__class__
	for pile in self.supported_piles():
	    str += u"%s pile: " % pile
	    if self.piles.get(pile) is None:
		str += u"missing\n"
	    else:
		str += u"{\n"
		place=0
		for card in self.piles[pile]:
		    place += 1
		    str += u"    %s. (%s) %s\n" % (place, card.id, card)
		str += u"}\n"
	return str

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

	# make sure we can look it up
	self.cards_by_id[card.id] = card

    # find a card object by its id
    def lookup_card(self,id):
	return self.cards_by_id[id]
	

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
	


# this just picks a random card from the deck, with no ideas of state
class RandomLearningModel(LearningModelBase):

    def choose_card(self):
	num = len(self.piles['Active'])
	which = random.randint(0,num-1)

	card = self.piles['Active'][which]
	return card


# Just goes through the cards in order.
class SimpleDeckModel(LearningModelBase):

    def choose_card(self):
	card = self.piles['Active'][0]

	# rotate the deck
	self.move_card_to_pile(card,'Active')
	#self.piles['Active'] = self.piles['Active'][1:]
	#self.piles['Active'].append(card)

	return card


# If you get a card right, put it at the back of the deck.
# If you get a card wrong, put it fairly close to the front
class BetterDeckModel(SimpleDeckModel):

    def supported_actions(self):
	return ['Yes','No','Discard']

    def supported_piles(self):
	return ['Active','Discard']
    
    # where to put the card if the user gets it wrong
    def how_far_back_when_wrong(self):
	return int(random.uniform(3,7))
	
    def log_impression(self,impression):
	#print u"better decklogging %s" % impression
	card = self.lookup_card(impression.concept_id)

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

