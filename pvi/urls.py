
from django.conf.urls import url
from pvi import http

urlpatterns = [
    #url(r'^pvi/query/$(pvi_name)/$(period_type)/$(info_name)', pvi.http.query),
    url(r'^query/(?P<pvi_name>\w+)/(?P<period_type>\w+)/(?P<info_name>\w+)/$', http.query),

]
