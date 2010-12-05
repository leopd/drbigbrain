from django.db import models
from django.conf import settings

#TODO: Make a "rights" object for each of these.
# The rights object is an owner, and a license.
# There's a base class which adds this functionality


#class RightsObject(Object)
    #rights = models.ForeignKey(Rights)
    #pass


#class Pixset(models.Model, RightsObject):
class Pixset(models.Model):
    description = models.CharField(max_length=100)
    # owner


class Pix(models.Model):
    img = models.ImageField(upload_to = settings.UPLOAD_DIR_PIX)
    # owner


class Lang(models.Model):
    """ A language descriptor.
    A node in a language hierarchy.
    """
    name = models.CharField(max_length = 50)
    parent = models.ForeignKey('self', null = True, blank = True)

    def __unicode__(self, prefix = ""):
        if self.parent:
            return "%s / %s" % (self.parent, self.name)
        else:
            return self.name


class Text(models.Model):
    # owner
    pix = models.ForeignKey(Pix)
    text = models.CharField(max_length = 100)
    form2 = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(Lang)
    

#class Voice
#   text =FK(text)

#class Accent
#   native = FK(lang)
#   level with this lang = Integer

