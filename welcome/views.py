from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import authenticate
from dbbpy.flashcards.models import Lesson

def homepage(request):
    return render_to_response("welcome/homepage.html", context_instance=RequestContext(request))

def chinese(request):
    lesson_list = Lesson.objects.all().order_by('name')
    return render_to_response("welcome/lessonlist.html", {'lessons': lesson_list} )

   
def register(request):
    data = request.POST.copy()
    form = UserCreationForm(data)

    if request.method == 'POST':
	if form.is_valid():
	    # create the new user
            new_user = form.save(data)

	    # now log them in
	    user = authenticate(username=data['username'], password=data['password1'] )
	    if user is not None: 
		login(request,user)
	    else:
		return HttpResponseRedirect("/loginfail")
		
	    if request.POST.get('next'):
		return HttpResponseRedirect(request.POST['next'])
	    else:
		return HttpResponseRedirect("/")

    return render_to_response("welcome/register.html", {
        'form' : form.as_p(),
    })

def ajaxloginlink(request):
    return render_to_response("welcome/ajaxloginlink.html", {
	'is_logged_in': request.user.is_authenticated(),
        'user' : request.user,
    })
    
