from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
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

    @staticmethod
    def for_request(request, create_new=True):
	"""Looks up the current deckstate for a request
	It tries to load it from the session first.
	If not there, it looks for one associated with this user.
	If none for this user, it might or might not create a new one,
	based on the input flag.
	If create_new is false, it will return None rather than create a new one 
	"""

	deckstate_id = request.session.get('deckstate_id')
	if deckstate_id is None:
	    # Nothing in the session.  See if we can find one for this user.
	    alldecks = DeckState.objects.filter(user = request.user)
	    if len(alldecks) == 0:
		# No deckstates for this user
		if not create_new:
		    return None
		else:
		    if request.user.__class__ == AnonymousUser:
			#TODO: someday we'll be able to just store it in session
			return None
		    deckstate = DeckState()
		    deckstate.user = request.user
		    deckstate.save() # to get the id
	    else:
		# Found deckstate(s) for this user from other sessions.
		# Arbitrarily picking the first one here
		deckstate = alldecks[0]

	    # put the id back in the session.
	    request.session['deckstate_id'] = deckstate.id

	else:
	    #print "get_model: deckstate_id in session is %s" % deckstate_id
	    deckstate = get_object_or_404(DeckState, pk=deckstate_id)

	return deckstate



