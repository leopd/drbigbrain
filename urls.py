from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^dbbpy/', include('dbbpy.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^dojango/', include('dojango.urls')),
    (r'^study/', include('study.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'welcome/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'welcome/logout.html'}),
    (r'^accounts/register/$', 'dbbpy.welcome.views.register'), 
    (r'', include('dbbpy.welcome.urls')),
)
