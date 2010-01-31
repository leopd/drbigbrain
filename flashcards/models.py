from django.db import models

class Concept(models.Model):
    description = models.CharField(max_length=200)

    def __unicode__(self):
	return self.description

class AssetType(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
	return self.name

class Asset(models.Model):
    asset_type = models.ForeignKey(AssetType)
    concept = models.ForeignKey(Concept)
    content = models.CharField(max_length=1000)

    def __unicode__(self):
	return self.content
