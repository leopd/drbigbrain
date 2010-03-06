from django.contrib import admin
from dbbpy.flashcards.models import Asset
from dbbpy.flashcards.models import AssetType
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.flashcards.models import LessonSequence

class AssetInline(admin.TabularInline):
    model = Asset
    extra = 1

class ConceptAdmin(admin.ModelAdmin):
    fieldsets = [
      (None, {'fields': ['description']}),
      ]
    inlines = [AssetInline]

class LessonSequenceInline(admin.TabularInline):
    model=LessonSequence
    extra = 1
    # blocks display of concept, which creates unbearably large inputs
    fieldsets = [
      (None, 
        {'fields': ['sequence']
        },
      ),
      ]
    #TODO: use a custom widget for concept selecting.
    # see http://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_overrides
    

class LessonAdmin(admin.ModelAdmin):
    inlines = [LessonSequenceInline]

admin.site.register(Asset)
admin.site.register(AssetType)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Lesson, LessonAdmin)
#admin.site.register(LessonSequence) # only needed for debugging

