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

@login_required
def studyui(request):
    return render_to_response("study/studyui.html", context_instance=RequestContext(request))


def getqa(request):
    # call the model to pick the next card to show
    model = request.session['learning_model']
    concept = model.choose_card()
    request.session['learning_model'] = model

    # TODO: generalize this for any lesson type
    q = concept.asset_set.get(asset_type=2).content
    a = u"<i>%s</i><br/>%s" % (
	    concept.asset_set.get(asset_type=3).content,
	    concept.asset_set.get(asset_type=4).content
	    )
    data = { "question": q, "answer": a, "concept": concept.id }
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def impression(request):
    # put this into a database table...
    i = Impression()
    #print request.POST
    i.answer = request.POST['answer']
    i.concept_id = long(request.POST['concept'])
    i.user = request.user
    i.save()

    # tell the learning model about the impression
    model = request.session['learning_model']
    concept = model.log_impression(i)
    request.session['learning_model'] = model

    # return a simple HTTP response
    return HttpResponse("OK", mimetype='text/plain')

@login_required
def setlesson(request,lesson_id):
    #model = RandomLearningModel()
    model = BetterDeckModel()
    model.set_active_lesson(lesson_id)
    request.session['learning_model'] = model
    return HttpResponseRedirect("/study/")
    
# print out the model state
def debugmodel(request):
    model = request.session['learning_model']
    return HttpResponse(model.__unicode__(), mimetype='text/plain')
    
