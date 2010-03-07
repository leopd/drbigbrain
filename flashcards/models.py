from django.db import models

class Concept(models.Model):
    """a concept is a unit of learning.
    for languages, this will be a word
    """

    description = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.description)

class AssetType(models.Model):
    """
    this describes the kind of content in an asset.
    it could describe the language of the content (i.e. spanish, english)
    or it could describe that the content is text or a URL of an image or sound
    etc.
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return unicode(self.name)

class Asset(models.Model):
    """
    this is a way to represent the concept.  it could be a definition in
    a language.  or anything else described by an assettype
    """
    asset_type = models.ForeignKey(AssetType)
    concept = models.ForeignKey(Concept)
    content = models.CharField(max_length=1000)

    def __unicode__(self):
        return unicode(self.content)


class Lesson(models.Model):
    """this is a way of grouping concepts together
    """
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=250)

    # the actual content
    concepts = models.ManyToManyField(Concept, through='LessonSequence')

    def __unicode__(self):
        return unicode(self.name)
    
class LessonSequence(models.Model):
    """many-many join table between lesson and concept
    Includes order
    """

    lesson = models.ForeignKey(Lesson)
    concept = models.ForeignKey(Concept)

    sequence = models.IntegerField(null = True)

    def __unicode__(self):
        if self.sequence == None:
            #return "lessonseq w/o seq"
            return u"Lesson(%s) Seq(-) is %s" % (self.lesson, self.concept)
        else:
            #return "lessonseq w/ seq"
            return u"Lesson(%s) Seq(%s) is %s" % (self.lesson, self.sequence, self.concept)

class FlashCard(models.Model):
    """This represents a canonical question/answer pair for user learning.
    It is fundamentally a Concept, but specificying a "view" for
    which part of the concept should be the question and which part
    the answer.

    e.g. A concept may have that "house" is english for "casa" in spanish.
    There would be two FlashCard objects, one with "house" as question
    and "casa" as answer, and another one with Q & A swapped.
    """
    #TODO: write
    pass
