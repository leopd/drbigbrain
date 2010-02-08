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

@login_required
def studyui(request):
    return render_to_response("study/studyui.html", context_instance=RequestContext(request))

def pick_concept(request):
    lesson = get_object_or_404(Lesson, pk=request.session['lesson'])
    num = lesson.concepts.count()
    which = random.randint(1,num)

    # note: this loads the entire lesson, which is unnecessarily slow.
    for concept in lesson.concepts.all():
	which = which-1
	if which==0:
	    return concept

    print "assertion fail. Should never get here in dbbpy.study.views.pick_concept"
    return None


def getqa(request):
    # pick a random card to show...
    concept = pick_concept(request)
    # TODO: generalize this for any lesson type
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
    i.user = request.user
    i.save()
    return HttpResponse("OK", mimetype='text/plain')

@login_required
def setlesson(request,lesson_id):
    request.session['lesson'] = lesson_id
    return HttpResponseRedirect("/study/")
    
