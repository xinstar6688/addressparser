from django.conf.urls.defaults import handler404, handler500, patterns
from address.views import AreaDetail

urlpatterns = patterns('',
    (r'^areas/([\w-]+)/$', AreaDetail())
)
