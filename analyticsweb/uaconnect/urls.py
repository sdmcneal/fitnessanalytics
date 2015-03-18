from django.conf.urls import patterns, url

from uaconnect import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^self/',views.selfview,name='selfview')
)