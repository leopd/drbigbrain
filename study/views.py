import json
import random
import cPickle as pickle
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import loader, Context, RequestContext
from django.contrib.auth.decorators import login_required
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.deck.models import Impression
from dbbpy.deck.models import DeckState
from dbbpy.deck.learning import RandomLearningModel
from dbbpy.deck.learning import SimpleDeckModel
from dbbpy.deck.learning import BetterDeckModel
from dbbpy.deck.learninghistory import HistoryModel

def get_model(request):
    """Returns the learningmodel object which is currently active.
    Returns None if there isn't one assicated with this user or session.
    """

    deckstate = DeckState.for_request(request,False)
    if deckstate is None:
	return None

    # Now we have a deckstate.  pull out the model
    p = deckstate.pickled_model
    if (p is None) or (p==""):
	return None

    # having problems with unicode pickling!
    # error -- KeyError: '\x00'
    p=str(p) # this seems to fix it
    #print "loading model from state %d pickled = %s" % (deckstate.id, p[0:50])
    model = pickle.loads(p)
    return model
    

def save_model(request, model):
    """Saves the learningmodel object back from whence it came
    """

    deckstate = DeckState.for_request(request,True)
    deckstate.pickled_model = pickle.dumps(model)

    # copy the model's description up to the deckstate
    deckstate.description = model.description
    deckstate.save()
    


@login_required
def studyui(request):
    """SHows the UI which presents cards and solicits the responses.
    This UI is all ajaxy and doesn't need any server-side data.
    #TODO: move this to static media
    """

    if get_model(request) is None:
	#TODO: generalize this to send you to a 'pick a lesson' page
	return HttpResponseRedirect("/chinese/")

    return render_to_response("study/studyui.html", context_instance=RequestContext(request))


def deckview(request):
    """Shows you a list of recent cards.
    """

    # first, fetch the recent impressions
    recent_impressions = Impression.objects.order_by('-answered_date').filter(user=request.user)
    # limit to last 30 impressions
    recent_impressions = recent_impressions[0:29]

    # now build a list of card Q's, with the pile for each card. 
    # don't eliminate duplicate cards
    model = get_model(request)
    recent_cards = []
    for impression in recent_impressions:
	#print "id %s" % impression.concept.id
	card = model.lookup_card(impression.concept.id)

	pile = model.which_pile(card)
	recent_cards.append( (card.question(), pile, card) )

    #
    # fetch counts for each pile
    #
    pilecount = []
    for pile in model.supported_piles():
	pilecount.append( (pile, len( model.cards_in_pile(pile) ) ) )

    # and the description
    description = model.description

    templatevars = {
	'recent_cards': recent_cards,
	'pilecount': pilecount,
	'description': description,
	}

    return render_to_response("study/deck.html", templatevars)
    
def dnddeckview(request):
    """Shows the old drag-n-drop deck view which doesn't do much
    """

    return render_to_response("study/dnddeck.html", context_instance=RequestContext(request))


def jsoncard(request, card_id):
    """Renders JSON for a single card
    TODO: HTTP-cache these, since they're immutable
    (THis is not actually used...)
    """

    model = get_model(request)
    card = model.lookup_card(card_id)
    data = card.json()
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def jsondeck(request):
    """Renders the entire deck in JSON for use with the dnd deckview
    """

    model = get_model(request)
    data = {}
    for pile in model.supported_piles():
	data[pile]=[]
	for card in model.cards_in_pile(pile):
	    data[pile].append( card.json() )

    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def getqa(request):
    """Returns the next card to display to the user.
    This is called frequently by the studyui.
    Guaranteed not to modify the model state -- it won't be saved!
    """

    # call the model to pick the next card to show
    model = get_model(request)
    card = model.choose_card()

    # Note: I'm changing the contract here.
    # Models aren't allowed to change their state when picking a card.
    # Picking a card has no side-effects.
    # This is not a big burden on the model, but greatly simplifies
    # the client.
    #save_model(request, model)

    data = card.json()
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

import time

def get_many_qa(request,numcards):
    """Fetches the next 'numcard' cards to be displayed. Similar to getqa.
    Returns a json array, with the first element being the sequence number
    and each subsequent element being a json card object.
    Allows smart client to pre-fetch multiple cards to minimize user latency.
    Guaranteed not to modify the model state -- it won't be saved!
    """

    # For testing slow/unreliable server...
    #time.sleep(3)
    #if random.uniform(0,1) < 0.5:
	#raise NotImplmentedError()

    # manually casting seems to avoid unicode wierdness
    numcards = int(numcards)

    model = get_model(request)

    # stash the sequence number at the beginning
    data = [ model.get_sequence() ]

    # ask the model for all the cards to show
    cards = model.choose_many_cards(numcards)

    for card in cards:
	data.append( card.json() )

    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )



def impression(request):
    """Logs that the user had an impression of a card.
    This is called frequently by the studyui.
    Turns user action into an Impression object.
    """

    # For testing slow/unreliable server...
    #time.sleep(3)

    # put this into a database table...
    i = Impression()
    #print request.POST
    i.answer = request.POST['answer']
    i.concept_id = long(request.POST['id'])
    i.user = request.user
    i.timer_show = request.POST['showtimer']
    i.timer_submit = request.POST['submittimer']
    i.save()

    #print "times: %s,%s ms" % (request.POST['showtime'], request.POST['submittime'])

    # tell the learning model about the impression
    model = get_model(request)
    concept = model.log_impression(i)
    save_model(request, model)

    # return a simple HTTP response
    return HttpResponse("OK", mimetype='text/plain')


# print out the model state
def debugmodel(request):
    """Dumps out the model in human-readable form.
    Also displays a form for allowing the debugger to post an impression and see
    any error message
    """

    model = get_model(request)
    str = u"%s" % model
    return render_to_response("study/debug.html", { 'debugstring': str } )
    

@login_required
def setlesson(request,lesson_id):
    """Adds this lesson to the active deck.
    """

    # put this lesson into the model
    model = get_model(request)
    if model is None:
	resetdeck(request)
	model = get_model(request)
    model.set_active_lesson(lesson_id)
    save_model(request, model)

    # send them off to study
    return HttpResponseRedirect("/study/")
    

def resetdeck(request):
    """Creates a new model object and saves it.
    This wipes out anything in the previous model.
    """

    #TODO: make this configurable
    #model = RandomLearningModel()
    #model = BetterDeckModel()
    model = HistoryModel()
    save_model(request, model)
    return HttpResponseRedirect("/")

