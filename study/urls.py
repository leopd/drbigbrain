from django.conf.urls.defaults import *

urlpatterns = patterns('study.views',
    (r'^$', 'studyui'),
    #(r'^deck$', 'deckview'),  # moved to deck module
    #(r'^dnddeck$', 'dnddeckview'),  # moved to deck module
    (r'^getqa$', 'getqa'),
    (r'^getqa-(?P<numcards>\d+)$', 'get_many_qa'),
    (r'^impression$', 'impression'),
    (r'^lesson/(?P<lesson_id>\d+)/$', 'setlesson'),
    (r'^debug$', 'debugmodel'),
    #(r'^jsondeck$', 'jsondeck'),  # moved to deck module
    (r'^jsoncard/(?P<card_id>\d+)$', 'jsoncard'),
    #(r'^resetdeck$', 'resetdeck'),  # moved to deck module
)
