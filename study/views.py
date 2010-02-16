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
from dbbpy.study.models import Impression
from dbbpy.study.models import DeckState
from dbbpy.study.learning import RandomLearningModel
from dbbpy.study.learning import SimpleDeckModel
from dbbpy.study.learning import BetterDeckModel
from dbbpy.study.learninghistory import HistoryModel

def get_model(request):
    """Returns the learningmodel object which is currently active.
    Returns None if there isn't one assicated with this user or session.
    """

    deckstate_id = request.session.get('deckstate_id')
    if deckstate_id is None:
	# Nothing in the session.  See if we can find one for this user.
	alldecks = DeckState.objects.filter(user = request.user)
	if len(alldecks) == 0:
	    return None
	# Arbitrarily picking the first one here
	deckstate = alldecks[0]

	# put the id back in the session.
	request.session['deckstate_id'] = deckstate.id

    else:
	#print "get_model: deckstate_id in session is %s" % deckstate_id
	deckstate = get_object_or_404(DeckState, pk=deckstate_id)

    # Now we have a deckstate.  pull out the model
    p = deckstate.pickled_model

    # having problems with unicode pickling!
    # error -- KeyError: '\x00'
    p=str(p) # this seems to fix it
    #print "loading model from state %d pickled = %s" % (deckstate_id, p[0:50])
    model = pickle.loads(p)
    return model
    

def save_model(request, model):
    """Saves the learningmodel object back from whence it came
    """

    deckstate_id = request.session.get('deckstate_id')
    if deckstate_id is None:
	# Create new deckstate object.
	deckstate = DeckState()
	deckstate.user = request.user
	deckstate.save() # to get the id
	request.session['deckstate_id']= deckstate.id
    else:
	# load the deckstate object
	deckstate = get_object_or_404(DeckState, pk=deckstate_id)

    deckstate.pickled_model = pickle.dumps(model)
    deckstate.save()
    


@login_required
def studyui(request):
    """SHows the UI which presents cards and solicits the responses.
    This UI is all ajaxy and doesn't need any server-side data.
    #TODO: move this to static media
    """

    return render_to_response("study/studyui.html", context_instance=RequestContext(request))


def deckview(request):
    """Shows you a list of recent cards.
    """

    # first, fetch the recent impressions
    recent_impressions = Impression.objects.order_by('-answered_date').filter(user=request.user)
    # limit to last 100 impressions
    recent_impressions = recent_impressions[0:99]

    # now build a list of card Q's, with the pile for each card. 
    # eliminating redundant cards
    model = get_model(request)
    cards_seen={}
    recent_cards = []
    for impression in recent_impressions:
	print "id %s" % impression.concept.id
	card = model.lookup_card(impression.concept.id)

	# remove redundant
	if not cards_seen.get(card.id):
	    cards_seen[card.id] = True
	    pile = model.which_pile(card)
	    recent_cards.append( (card.question(), pile, card) )
    # limit to most recent 30
    recent_cards = recent_cards[0:29]

    #
    # fetch counts for each pile
    #
    pilecount = []
    for pile in model.supported_piles():
	pilecount.append( (pile, len( model.cards_in_pile(pile) ) ) )

    templatevars = {
	'recent_cards': recent_cards,
	'pilecount': pilecount,
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
    This is called frequently by the studyui
    """

    # call the model to pick the next card to show
    model = get_model(request)
    card = model.choose_card()
    save_model(request, model)

    data = card.json()
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def impression(request):
    """Logs that the user had an impression of a card.
    This is called frequently by the studyui.
    Turns user action into an Impression object.
    """

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

    model = get_model(request)
    if model is None:
	resetdeck(request)
	model = get_model(request)
    model.set_active_lesson(lesson_id)
    save_model(request, model)
    return HttpResponseRedirect("/study/")
    

def resetdeck(request):
    """Clears the active deck.
    """

    #TODO: make this configurable
    #model = RandomLearningModel()
    #model = BetterDeckModel()
    model = HistoryModel()
    save_model(request, model)
    return HttpResponseRedirect("/")

