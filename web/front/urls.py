from django.conf.urls import url

from front import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^player/add/$', views.player_add, name='player_add'),
    url(r'^player/(?P<id>[0-9]+)/$', views.player, name='player'),
    url(r'^player/(?P<id>[0-9]+)/del/$', views.player_del, name='player_del'),
]
