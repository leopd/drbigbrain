from django.conf.urls.defaults import *

urlpatterns = patterns('welcome.views',
    (r'^$', 'homepage'),
    (r'^chinese/$', 'chinese'),
    (r'^ajaxloginlink$', 'ajaxloginlink'),
    (r'^about$', 'about'),
)
