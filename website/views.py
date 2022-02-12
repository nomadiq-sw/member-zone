from django.views.generic import FormView, TemplateView
from django.shortcuts import render


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


def alt_index(request):
    return render(request, 'alt-index.html')
