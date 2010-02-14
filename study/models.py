from django.db import models
from django.contrib.auth.models import User
from dbbpy.flashcards.models import Concept

class Impression(models.Model):
    """Records an Impression of a card on a user.
    That is, it records what card the user saw, when and their response.
    """

    user = models.ForeignKey(User)
    concept = models.ForeignKey(Concept)
    #TODO: add card instead of (as well as?) concept
    answered_date = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=10)

    timer_show = models.IntegerField(null = True)
    timer_submit = models.IntegerField(null = True)

    def __unicode__(self):
	return u"Impression on %s '%s'" % (self.concept,self.answer)


class DeckState(models.Model):
    """Stores state of studying for a user.
    This is similar to django_session, but works across browsers.
    A user might have several of these simultaneously.
    """

    user = models.ForeignKey(User)
    description = models.CharField(max_length=100, null=True)
    pickled_model = models.TextField()
    last_accessed = models.DateTimeField(auto_now=True)
