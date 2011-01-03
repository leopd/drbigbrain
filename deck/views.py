try: import simplejson as json
except ImportError: import json
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from deck.models import Impression
from deck.models import DeckState

#from deck.learning import RandomLearningModel
#from deck.learning import SimpleDeckModel
#from deck.learning import BetterDeckModel
#from deck.learninghistory import HistoryModel as ActiveModel
from deck.learningtime import TimeModel as ActiveModel


from deck.models import get_model, save_model
from deck.card import Card


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
        card = Card.lookup_card(impression.concept.id)

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
    # This is the single method which determines what kind of model will be used.

    #TODO: make this configurable
    #model = RandomLearningModel()
    #model = BetterDeckModel()
    #model = HistoryModel()
    model = ActiveModel()
    save_model(request, model)
    return HttpResponseRedirect("/")



def make_review_ui(request):
    """Shows UI for the user to create a review deck
    """

    return render_to_response("deck/make_review_ui.html", context_instance=RequestContext(request))


def create_review_deck(request):
    """ Creates a deck forreviewing old material.
    Wipes out the current deck 
    """

    # start over with a new model
    resetdeck(request)
    model = get_model(request)

    # Fetch a bunch of impressions
    all_no = Impression.objects.filter(user=request.user, answer="No")
    all_kinda = Impression.objects.filter(user=request.user, answer="Kinda")

    # add up the bad impressions
    bad_total = {}
    for impression in all_kinda:
        id = impression.concept_id
        # TUNE: 1 point per kinda
        if id not in bad_total:
            bad_total[ impression.concept_id ] = 1
        else:
            bad_total[ impression.concept_id ] += 1
    for impression in all_no:
        id = impression.concept_id
        # TUNE: 3 points per no
        if id not in bad_total:
            bad_total[ impression.concept_id ] = 3
        else:
            bad_total[ impression.concept_id ] += 3

    # invert the map so it maps # bad points to concepts.
    # Note there could be collisions here, so build a list for each num pts
    inverted_bad_total = {}
    for id, pts in bad_total.items():
        # TUNE: Minimum threshhold for something to be reviewable
        if pts > 2:
            if pts not in inverted_bad_total:
                inverted_bad_total[pts]=[id]
            else:
                inverted_bad_total[pts].append(id)
    
    # Prepare results list
    review_cards = []

    # Now we put together our list of cards, in order of badness
    print "ibt: %s" % inverted_bad_total
    pts_order_desc = inverted_bad_total.keys()
    pts_order_desc.reverse()
    print "pod: %s" % pts_order_desc
    for pts in pts_order_desc:
        for card in inverted_bad_total[pts]:
            review_cards.append(card)
        
    # Now put them all into the model
    model.add_new_cards("Review of difficult cards", review_cards)

    # Write the model back
    save_model(request,model)

    # redirect to a standard deck view
    return HttpResponseRedirect("/deck/")

