from django.conf.urls import url

from front import views

urlpatterns = [
    url(r'^user/$', views.user, name='user'),
    url(r'^player/add/$', views.player_add, name='player_add'),
    url(r'^player/(?P<id>[0-9]+)/$', views.player, name='player'),
    url(r'^result/(?P<id>[0-9]+)/$', views.result, name='result'),
    url(r'^player/(?P<id>[0-9]+)/del/$', views.player_del, name='player_del'),
    url(r'^round/(?P<id>[0-9]+)/$', views.round, name='round'),
    url(r'^$', views.rounds, name='rounds'),
]
