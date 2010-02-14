from django.db import models
from django.contrib.auth.models import User
from dbbpy.flashcards.models import Concept

class Impression(models.Model):
    user = models.ForeignKey(User)
    concept = models.ForeignKey(Concept)
    #TODO: add card instead of (as well as?) concept
    answered_date = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=10)

    timer_show = models.IntegerField(null = True)
    timer_submit = models.IntegerField(null = True)

    def __unicode__(self):
	return u"Impression on %s '%s'" % (self.concept,self.answer)

