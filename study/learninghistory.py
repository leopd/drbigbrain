import random
from dbbpy.study.learning import SimpleDeckModel
from dbbpy.study.learning import LearningModelBase



# Considers the history 
class HistoryModel(SimpleDeckModel):

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
	self.model_seq += 1
	print "model seq up to %s" % self.model_seq

	card = self.front_of_pile('Learning')
	if (card != None ) and (not self.too_soon(card)):
	    print "from learning pile"
	    return card
	print "Nothing good in learning pile"
	
	card = self.front_of_pile('Review')
	if (card != None ) and (not self.too_soon(card)):
	    print "from review pile"
	    return card
	print "Nothing good in review pile"
	
	card = self.front_of_pile('Unseen')
	if (card != None ):
	    print "from new pile"
	    return card
	print "Nothing at all in unseen pile"

	
	card = self.front_of_pile('Learning')
	if (card != None ):
	    print "backup from learning pile"
	    return card
	print "Nothing at all in learning pile"
	
	card = self.front_of_pile('Review')
	if (card != None ):
	    print "backup from review pile"
	    return card
	print "Nothing at all in review pile"
	
	raise NotImplementedError("can't find any more to do in deck")


    def log_impression(self,impression):
	card = self.lookup_card(impression.concept_id)
	next_status = self.get_next_card_status(card,impression.answer)
	self.move_card_to_pile(card,next_status)
	self.calculate_soonest(card)
    
	card.log_impression(impression)


    def get_next_card_status(self,card,answer):
	history = card.history()
	previous_answer = history.previous_answer()
	previous_status = self.which_pile(card)

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
		    if history.no_count() <= 1:
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
	return None


    # figures out how long we should wait before showing this card again
    def calculate_soonest(self,card):
	status = self.which_pile(card)
	if status == 'Learning':
	    #TODO: make this vary with history
	    delay = random.uniform(5,10)
	elif status == 'Review':
	    #TODO: make this vary with history
	    delay = random.uniform(10,30)
	else:
	    delay = 100
	self.soonest[card.id] = self.model_seq + delay

	# resort this list if it matters
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

	print u"Card too soon? %s < %s (%s)" % (self.model_seq, soonest, card)
	return self.model_seq < soonest

    def set_active_lesson(self,lesson_id):
	#TODO: make this less hacky
	LearningModelBase.set_active_lesson(self,lesson_id)
	for card in self.piles['Active']:
	    self.piles['Unseen'].append(card)
	del self.piles['Active']
	
