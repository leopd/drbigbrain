from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.study.views',
    (r'^$', 'studyui'),
    (r'^deck$', 'deckview'),
    (r'^dnddeck$', 'dnddeckview'),
    (r'^getqa$', 'getqa'),
    (r'^getqa-(?P<numcards>\d+)$', 'get_many_qa'),
    (r'^impression$', 'impression'),
    (r'^lesson/(?P<lesson_id>\d+)/$', 'setlesson'),
    (r'^debug$', 'debugmodel'),
    (r'^jsondeck$', 'jsondeck'),
    (r'^jsoncard/(?P<card_id>\d+)$', 'jsoncard'),
    (r'^resetdeck$', 'resetdeck'),
)
