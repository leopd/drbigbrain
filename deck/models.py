import cPickle as pickle
import base64
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from flashcards.models import Concept

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
        return u"Impression at %s: %s on %s" % (self.answered_date, self.answer,self.concept)


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
            if request.user.__class__ == AnonymousUser:
                #TODO: someday we'll be able to just store it in session
                return None
            # Nothing in the session.  See if we can find one for this user.
            alldecks = DeckState.objects.filter(user = request.user)
            if len(alldecks) == 0:
                # No deckstates for this user
                if not create_new:
                    return None
                else:
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
            # Try to get the referenced deckstate object.
            try:
                deckstate = DeckState.objects.get(pk=deckstate_id)
            except DeckState.DoesNotExist:
                # DeckState must have been deleted.  Reset the session.
                request.session['deckstate_id'] = None
                deckstate = None
                
        return deckstate

    
def get_model(request):
    """Returns the learningmodel object which is currently active.
    Returns None if there isn't one assicated with this user or session.
    Tries to find one in the session or for this user.
    Does not create a new model.
    """

    deckstate = DeckState.for_request(request,False)
    if deckstate is None:
        return None

    # Now we have a deckstate.  pull out the model
    p = deckstate.pickled_model
    if (p is None) or (p==""):
        return None

    # having problems with unicode pickling!
    # error -- KeyError: '\x00'
    #p=str(p) # this seems to fix it

    # Now it's saying "incorrect string value"
    p = base64.b64decode(p)
    #print "loading model from state %d pickled = %s" % (deckstate.id, p[0:50])
    model = pickle.loads(p)
    return model
    

def save_model(request, model):
    """Saves the learningmodel object back from whence it came
    Creates a new model (deckstate) if necessary.
    """

    deckstate = DeckState.for_request(request,True)
    p = pickle.dumps(model)
    deckstate.pickled_model = base64.b64encode(p)


    # copy the model's description up to the deckstate
    deckstate.description = model.description
    deckstate.save()
    




