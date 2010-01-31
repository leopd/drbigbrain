from django.contrib import admin
from dbbpy.flashcards.models import Asset
from dbbpy.flashcards.models import AssetType
from dbbpy.flashcards.models import Concept

class AssetInline(admin.TabularInline):
    model = Asset
    extra = 3

class ConceptAdmin(admin.ModelAdmin):
    #fields = ['pub_date', 'question']
    fieldsets = [
      (None, {'fields': ['description']}),
      ]
    inlines = [AssetInline]
    #list_display = ('question', 'pub_date', 'was_published_today')
    #list_filter = ['pub_date']
    #search_fields = ['question']
    #date_hierarchy = 'pub_date'

admin.site.register(Asset)
admin.site.register(AssetType)
admin.site.register(Concept, ConceptAdmin)

