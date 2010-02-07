from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext

def showcard(request):
    return render_to_response("study/showcard.html", context_instance=RequestContext(request))

def getqa(request):
    return render_to_response("study/getqa.html", context_instance=RequestContext(request))

def impression(request):
    return render_to_response("study/impression.html", context_instance=RequestContext(request))
