from django.db import models

# a concept is a unit of learning.
# for languages, this will be a word
class Concept(models.Model):
    description = models.CharField(max_length=200)

    def __unicode__(self):
	return self.description

# this describes the kind of content in an asset.
# it could describe the language of the content (i.e. spanish, english)
# or it could describe that the content is text or a URL of an image or sound
# etc.
class AssetType(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
	return self.name

# this is a way to represent the concept.  it could be a definition in
# a language.  or anything else described by an assettype
class Asset(models.Model):
    asset_type = models.ForeignKey(AssetType)
    concept = models.ForeignKey(Concept)
    content = models.CharField(max_length=1000)

    def __unicode__(self):
	return self.content


# this is a way of grouping concepts together
class Lesson(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=250)

    # for organization
    parent = models.ForeignKey('self') # TODO: consider using treebeard or similar
    sequence = models.IntegerField()

    concepts = models.ManyToManyField(Concept)
    # see http://docs.djangoproject.com/en/dev/topics/db/models/#intermediary-manytomany

    def __unicode__(self):
	return self.name
    
