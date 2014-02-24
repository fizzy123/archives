from django.conf.urls import patterns, url

from archives import views

urlpatterns = patterns('archives.views',
        url(r'^process/(?P<text>[^\t\n\r\f\v/]+)/$', 'process', name='process'),
        url(r'^show/(?P<name>[^ \t\n\r\f\v/]+)/$', 'show', name='show'),
        )

