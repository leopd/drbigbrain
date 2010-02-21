import json
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
from dbbpy.deck.models import get_model, save_model
# Create your views here.

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

