from django.views.generic.simple import direct_to_template, redirect_to
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^study/', include('study.urls')),
    (r'^deck/', include('deck.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'welcome/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'welcome/logout.html'}),
    (r'^accounts/register/$', 'welcome.views.register'), 
    (r'', include('welcome.urls')),

    (r'^robots.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    # dev hack
    (r'^static/jquery.hotkeys.js$', redirect_to, {'url': 'https://github.com/jeresig/jquery.hotkeys/raw/master/jquery.hotkeys.js'}),

)


