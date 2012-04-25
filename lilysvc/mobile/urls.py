from django.conf.urls.defaults import *

from lilysvc.mobile.views import *

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^boardlist$', boardlist, name='boardlist'),
    url(r'^top10$', top10, name='top10'),
    url(r'^hot$', hot, name='hot'),
    url(r'^board/(?P<board>\w+)(/(?P<start>\d+))?$', board, name='board'),
    url(r'^topic/(?P<board>\w+)/(?P<pid>\d+)$', topic, name='topic'),
    url(r'^api/board/(?P<board>\w+)(/(?P<start>\d+))?$', api_board),
    url(r'^api/topic/(?P<board>\w+)/(?P<pid>\d+)(/(?P<start>\d+))?$', api_topic),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^about/$', about, name='about'),
)

