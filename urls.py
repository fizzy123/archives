from django.conf.urls import patterns, url

from archives import views

urlpatterns = patterns('archives.views',
        url(r'^$', 'index', name='index'),
        url(r'^receive/$', 'recieve', name='recieve'),
        url(r'^reply/$', 'reply', name='reply'),
#        url("", include('django_socketio.urls'))
        )

