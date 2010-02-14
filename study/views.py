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
	alldecks = DeckState.objects.filter(user = request.user)
	if len(alldecks) == 0:
	    return None
	# Arbitrarily picking the first one here
	deckstate = alldecks[0]
    else:
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


# UI to manage the active deck
def deckview(request):
    """Shows UI to manually manipulate the state of the deck
    """

    return render_to_response("study/deck.html")
    

def card_as_json(concept):
    """Renders a single card as json
    TODO: generalize this for any lesson type
    # move this logic for picking assettypes into Card class
    """

    q = concept.asset_set.get(asset_type=2).content
    a = u"<i>%s</i><br/>%s" % (
	    concept.asset_set.get(asset_type=3).content,
	    concept.asset_set.get(asset_type=4).content
	    )
    data = { 
	"question": q, 
	"answer": a, 
	"id": concept.id,
	"summary": unicode(concept),
	}
    return data


def jsoncard(request, card_id):
    """Renders JSON for a single card
    TODO: HTTP-cache these, since they're immutable
    """

    concept = get_object_or_404(Concept, pk=card_id)
    data = card_as_json(concept)
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def jsondeck(request):
    """Renders the entire deck in JSON for use with the deckview
    """

    model = get_model(request)
    data = {}
    for pile in model.supported_piles():
	data[pile]=[]
	for card in model.cards_in_pile(pile):
	    concept = card.concept()
	    data[pile].append( card_as_json(concept) )

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
    concept = model.choose_concept()
    save_model(request, model)

    data = card_as_json(concept)
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

