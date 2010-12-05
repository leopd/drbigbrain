from django.contrib import admin

import pixset.models as m

class PixInline(admin.TabularInline):
    model = m.Text
    #extra = 1

#class ConceptAdmin(admin.ModelAdmin):
    #fieldsets = [
      #(None, {'fields': ['description']}),
      #]
    #inlines = [AssetInline]


class PixAdmin(admin.ModelAdmin):
    inlines = [PixInline]

admin.site.register(m.Pix, PixAdmin)
admin.site.register(m.Lang)
