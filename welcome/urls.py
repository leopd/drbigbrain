from django.conf.urls.defaults import *

urlpatterns = patterns('dbbpy.welcome.views',
    (r'^$', 'homepage'),
    (r'^chinese/$', 'chinese'),
)
