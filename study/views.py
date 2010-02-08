import json
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import loader, Context, RequestContext
from django.contrib.auth.decorators import login_required
from dbbpy.flashcards.models import Concept
from dbbpy.study.models import Impression

def studyui(request):
    return render_to_response("study/studyui.html", context_instance=RequestContext(request))

def pick_concept():
    num = Concept.objects.count()
    which = random.randint(1,num/10) # /10 to make it easier
    #TODO: this won't work if the id space isn't dense
    concept = get_object_or_404(Concept, pk=which)
    return concept


def getqa(request):
    # pick a random card to show...
    concept = pick_concept()
    # TODO: make this less hacky
    q = concept.asset_set.get(asset_type=2).content
    a = concept.asset_set.get(asset_type=4).content
    data = { "question": q, "answer": a, "concept": concept.id }
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def impression(request):
    # put this into a database table...
    i = Impression()
    print request.POST
    i.answer = request.POST['answer']
    i.concept_id = request.POST['concept']
    i.save()
    return HttpResponse("OK", mimetype='text/plain')

@login_required
def setlesson(request,lesson_id):
    return HttpResponseRedirect("/study/")
    
