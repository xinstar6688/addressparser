from django.conf.urls.defaults import patterns
from address.services import AreaResource

urlpatterns = patterns('',
    (r'^areas/([\w-]+)/$', AreaResource())
)
