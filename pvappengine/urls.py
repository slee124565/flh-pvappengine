"""pvappengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin

from pvappengine import http_api as appeng_http_api

from accuweather.views import accuweather_geo_location_search,accuweather_location_key_geo_search

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^pvs_meta/$', appeng_http_api.query_pvs_meta  ),
    url(r'^pvs_meta/(?P<pvi_name>\w+)/$', appeng_http_api.query_pvs_meta  ),
    
    url(r'^amchart/$', appeng_http_api.query_chart_data  ),
    url(r'^amchart/(?P<data_type>\w+)/$', appeng_http_api.query_chart_data  ),

    url(r'^accu/geo_search/', accuweather_geo_location_search  ),
    url(r'^accu/key_geo_search/', accuweather_location_key_geo_search  ),
    
    url(r'^dbclean/$', appeng_http_api.clean_db  ),
]
