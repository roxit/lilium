from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^fetch/', 'fetch.fetch'),
    (r'^api/', include('api.urls')),
)


import os

from django.conf import settings


if 'APP_NAME' not in os.environ:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

