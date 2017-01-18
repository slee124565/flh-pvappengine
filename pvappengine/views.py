from django.views.generic import TemplateView, View
from django.http.response import HttpResponse, Http404
from django.conf import settings

import os


class DefaultView(TemplateView):
    
    template_name = 'index.html'
    
class AngularTemplateView(View):

    def get(self, request, item=None, *args, **kwargs):
        #print(item)
        #template_dir_path = settings.TEMPLATES[0]["DIRS"][0]
        final_path = os.path.join(settings.BASE_DIR,'ngapp','app','views',item+".html" )
        try:
            html = open(final_path)
            return HttpResponse(html)
        except:
            raise Http404
    