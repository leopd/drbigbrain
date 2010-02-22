from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.deck.views',
    (r'^$', 'deckview'),
    (r'^reset$', 'resetdeck'),
    (r'^dnddeck$', 'dnddeckview'),
    (r'^jsondeck$', 'jsondeck'),
    (r'^review$', 'make_review_ui'),
    (r'^create_review_deck$', 'create_review_deck'),
)

