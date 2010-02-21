from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.deck.views',
    (r'^$', 'deckview'),
    (r'^reset$', 'resetdeck'),
    (r'^dnddeck$', 'dnddeckview'),
    (r'^jsondeck$', 'jsondeck'),
)

