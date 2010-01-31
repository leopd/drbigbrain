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

class LessonAdmin(admin.ModelAdmin):
    inlines = [LessonSequenceInline]

admin.site.register(Asset)
admin.site.register(AssetType)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonSequence)

