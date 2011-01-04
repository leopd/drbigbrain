from django.conf.urls.defaults import *

urlpatterns = patterns('deck.views',
    #(r'^$', 'deckview'),
    (r'^$', 'show_meta'),
    (r'^reset$', 'resetdeck'),
    (r'^dnddeck$', 'dnddeckview'),
    (r'^jsondeck$', 'jsondeck'),
    (r'^review$', 'make_review_ui'),
    (r'^create_review_deck$', 'create_review_deck'),
    (r'^show_meta$', 'show_meta'),
)

