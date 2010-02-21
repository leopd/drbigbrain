import json
import cPickle as pickle
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from dbbpy.deck.models import Impression
from dbbpy.deck.models import DeckState
from dbbpy.deck.learning import RandomLearningModel
from dbbpy.deck.learning import SimpleDeckModel
from dbbpy.deck.learning import BetterDeckModel
from dbbpy.deck.learninghistory import HistoryModel
# Create your views here.

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

    return render_to_response("deck/deckview.html", templatevars)
    
def dnddeckview(request):
    """Shows the old drag-n-drop deck view which doesn't do much
    """

    return render_to_response("deck/dnddeck.html", context_instance=RequestContext(request))


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

