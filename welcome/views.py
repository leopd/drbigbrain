from django.template import RequestContext
from django.shortcuts import render_to_response
from dbbpy.flashcards.models import Lesson

def homepage(request):
    return render_to_response("welcome/homepage.html", context_instance=RequestContext(request))

def chinese(request):
    lesson_list = Lesson.objects.all().order_by('name')
    return render_to_response("welcome/lessonlist.html", {'lessons': lesson_list} )

   
