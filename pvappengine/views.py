from django.views.generic import TemplateView
from django.http.response import HttpResponse


class DefaultView(TemplateView):
    
    template_name = 'index.html'
    