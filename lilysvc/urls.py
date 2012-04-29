from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^fetch/', 'lilysvc.fetch.fetch'),
    (r'^', include('lilysvc.mobile.urls')),
)

import os

from django.conf import settings

if 'APP_NAME' not in os.environ:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    )

