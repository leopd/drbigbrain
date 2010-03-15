from django.db import models
from django.template import Context, Template

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


class FlashCardType(models.Model):
    """A way of displaying a concept as a flashcard.
    Specifies which assettypes for question, answer.
    Also how to render them in HTML.
    Includes methods for rendering question and answer.
    """
    name = models.CharField(max_length=30)
    asset_types = models.ManyToManyField(AssetType, through='AssetUsedInCardType')
    question_template = models.CharField(max_length=500, null=True)
    answer_template = models.CharField(max_length=500, null=True)

    def __unicode__(self):
	return self.name

    def render_html(self,template_str,card):
	"""Substitutes the card's assets into the template.
	"""

	#TODO: test this!

	# Make a dictionary of the assets in the card
	# by going through the asset_types list.
	dict = {}
	assets = card.concept.asset_set
	# Find all the appropriate AssetUsedInCardType objects
	qs = AssetUsedInCardType.objects.filter(flash_card_type = self)
	for asset_used in qs:
	    token = asset_used.token
	    asset = assets.get(asset_type = asset_used.asset_type)
	    dict[ token ] = asset

	# Run it through the django template
	# See http://docs.djangoproject.com/en/dev/ref/templates/api/
	template = Template(template_str)
	context = Context(dict)
	html = template.render(context)
	return html


    def html_question(self,card):
	"""Returns HTML rendered question for the specified card
	"""
	return self.render_html(self.question_template,card)


    def html_answer(self,card):
	"""Returns HTML rendered answer for the specified card
	"""
	return self.render_html(self.answer_template,card)


class AssetUsedInCardType(models.Model):
    """Many to many join table between FlashCardType and AssetType.
    Carries an identifying string along with the connection.
    This string is used in the template formating.
    """

    flash_card_type = models.ForeignKey(FlashCardType)
    asset_type = models.ForeignKey(AssetType)

    token = models.CharField(max_length=10)

    def __unicode__(self):
	return "%s.%s" % (self.flash_card_type, self.token)


class FlashCard(models.Model):
    """A canonical question/answer pair for user learning.
    It is fundamentally a Concept, but specificying a "view" for
    which part of the concept should be the question and which part
    the answer.

    e.g. A concept may have that "house" is english for "casa" in spanish.
    There would be two FlashCard objects, one with "house" as question
    and "casa" as answer, and another one with Q & A swapped.
    """
    #This replaces the 'deck.Card' class, which was coupled to a user.

    concept = models.ForeignKey(Concept)
    cardtype = models.ForeignKey(FlashCardType)

    def __unicode__(self):
	return u"%s (%s)" % (self.concept, self.cardtype)

    def html_question(self):
	"""Returns HTML rendered question for this card
	"""
	return self.cardtype.html_question(self)


    def html_answer(self):
	"""Returns HTML rendered answer for this card
	"""
	return self.cardtype.html_answer(self)


