import json
import random
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import loader, Context, RequestContext
from django.contrib.auth.decorators import login_required
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.study.models import Impression
from dbbpy.study.learning import RandomLearningModel
from dbbpy.study.learning import SimpleDeckModel
from dbbpy.study.learning import BetterDeckModel
from dbbpy.study.learninghistory import HistoryModel

def get_model(request):
    return request.session['learning_model']
    

def save_model(request, model):
    request.session['learning_model'] = model
    


@login_required
def studyui(request):
    #TODO: move this to static media
    return render_to_response("study/studyui.html", context_instance=RequestContext(request))


# UI to manage the active deck
def deckview(request):
    return render_to_response("study/deck.html")
    

def card_as_json(concept):
    # TODO: generalize this for any lesson type
    # move this into Card class
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
    concept = get_object_or_404(Concept, pk=card_id)
    data = card_as_json(concept)
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def jsondeck(request):
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
    # put this into a database table...
    i = Impression()
    #print request.POST
    i.answer = request.POST['answer']
    i.concept_id = long(request.POST['id'])
    i.user = request.user
    i.save()

    # tell the learning model about the impression
    model = get_model(request)
    concept = model.log_impression(i)
    save_model(request, model)

    # return a simple HTTP response
    return HttpResponse("OK", mimetype='text/plain')


# print out the model state
def debugmodel(request):
    model = get_model(request)
    str = u"%s" % model
    return render_to_response("study/debug.html", { 'debugstring': str } )
    

@login_required
def setlesson(request,lesson_id):
    model = get_model(request)
    if model is None:
	self.resetdeck(request)
    model.set_active_lesson(lesson_id)
    save_model(request, model)
    return HttpResponseRedirect("/study/")
    

def resetdeck(request):
    #TODO: make this configurable
    #model = RandomLearningModel()
    #model = BetterDeckModel()
    model = HistoryModel()
    save_model(request, model)
    return HttpResponseRedirect("/")

