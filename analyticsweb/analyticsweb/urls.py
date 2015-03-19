from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'analyticsweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ua/',include('uaconnect.urls')),
#    url(r'^oauth2/',include('provider.oauth2.urls', namespace = 'oauth2')),
)
