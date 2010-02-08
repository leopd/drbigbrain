from django.db import models
from django.contrib.auth.models import User
from dbbpy.flashcards.models import Concept

class Impression(models.Model):
    #TODO: these two should not actually be allowed to be null
    user = models.ForeignKey(User, null=True)
    concept = models.ForeignKey(Concept, null=True)
    #TODO: add card instead of (as well as?) concept
    answered_date = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=10)

