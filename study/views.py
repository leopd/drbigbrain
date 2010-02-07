from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext

def showcard(request):
    return render_to_response("study/showcard.html", context_instance=RequestContext(request))
