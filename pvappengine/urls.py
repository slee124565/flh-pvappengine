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

from pvi import http_api as pvi_http_api
from pvappengine import http_api as appeng_http_api

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^pvi/', include('pvi.urls')),
    
    url(r'^appeng/pvs_meta/$', appeng_http_api.query_pvs_meta  ),
    url(r'^appeng/pvs_meta/(?P<pvi_name>\w+)/$', appeng_http_api.query_pvs_meta  ),
    
    url(r'^appeng/amchart/$', appeng_http_api.query_chart_data  ),
    url(r'^appeng/amchart/(?P<data_type>\w+)/$', appeng_http_api.query_chart_data  ),

]
