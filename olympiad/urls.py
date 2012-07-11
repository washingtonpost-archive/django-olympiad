from django.conf.urls.defaults import patterns, include

from olympiad.api import v1

urlpatterns = patterns('',
    (r'^api/', include(v1.urls)),
)
