from django.conf.urls.defaults import *

from lilysvc.mobile.views import *

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^about/$', about, name='about'),
    url(r'^api/board/(?P<board>\w+)(/(?P<start>\d+))?/$', api_board),
    url(r'^api/topic/(?P<board>\w+)/(?P<pid>\d+)(/(?P<start>\d+))?/$', api_topic),
    url(r'^board/(?P<board>\w+)(/(?P<start>\d+))?/$', board, name='board'),
    url(r'^compose/(?P<board>\w+)/$', compose, name='compose'),
    url(r'^hot/$', hot, name='hot'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^section/(?P<sid>\d+)/$', section, name='section'),
    url(r'^top10/$', top10, name='top10'),
    url(r'^topic/(?P<board>\w+)/(?P<pid>\d+)/$', topic, name='topic'),
)

