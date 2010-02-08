from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.study.views',
    (r'^$', 'studyui'),
    (r'^getqa$', 'getqa'),
    (r'^impression$', 'impression'),
    (r'^lesson/(?P<lesson_id>\d+)/$', 'setlesson'),
)
