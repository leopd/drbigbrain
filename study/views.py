import json
import random
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import loader, Context, RequestContext
from dbbpy.flashcards.models import Concept

def studyui(request):
    return render_to_response("study/studyui.html", context_instance=RequestContext(request))

def pick_concept():
    num = Concept.objects.count()
    which = random.randint(1,num)
    # this won't work if the id space isn't dense
    concept = get_object_or_404(Concept, pk=which)
    return concept


def getqa(request):
    # pick a random card to show...
    concept = pick_concept()
    # TODO: make this less hacky
    q = concept.asset_set.get(asset_type=2).content
    a = concept.asset_set.get(asset_type=4).content
    data = { "question": q, "answer": a }
    return HttpResponse(
		    json.dumps(data),
                    mimetype='text/plain'
		    )

def impression(request):
    # put this into a database table...
    return render_to_response("study/impression.html", context_instance=RequestContext(request))
