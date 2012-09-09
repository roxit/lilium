from django.conf.urls.defaults import *

from api.views import *

urlpatterns = patterns('',
    url(r'^board/(?P<board>\w+)(/(?P<idx>\d+))?/$', PageView.as_view(), name='api_board'),
    url(r'^post/(?P<board>\w+)(/(?P<pid>\d+))?/$', PostView.as_view(), name='api_post'),
    url(r'^hot/$', HotView.as_view(), name='api_hot'),
    url(r'^top/$', TopView.as_view(), name='api_top'),
    url(r'^topic/(?P<board>\w+)/(?P<pid>\d+)(/(?P<idx>\d+))?/$', TopicView.as_view(), name='api_topic'),
    url(r'^login/', LogInView.as_view(), name='api_login'),
    url(r'^logout/', LogOutView.as_view(), name='api_logout'),
    url(r'^subscription/', SubscriptionView.as_view(), name='api_subscription')
)

