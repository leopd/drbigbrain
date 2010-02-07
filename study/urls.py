from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.study.views',
    (r'^$', 'showcard'),
    (r'^getqa$', 'getqa'),
    (r'^impression$', 'impression'),
    #(r'^(?P<poll_id>\d+)/$', 'detail'),
    #(r'^(?P<poll_id>\d+)/results/$', 'results'),
    #(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
)
